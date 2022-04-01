import { Component, HostListener, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatStepper, StepperOrientation } from '@angular/material/stepper';
import { CountdownComponent, CountdownEvent } from 'ngx-countdown';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import * as moment from 'moment';
import config from '../../config.json';

import { LabService } from 'src/app/services/lab.service';
import { KitService } from 'src/app/services/kit.service';
import { ToastrService } from 'ngx-toastr';
import { ComponentCanDeactivate } from '../../pending-changes.guard';

import { AvailableDate } from 'src/app/interfaces/available-date';
import { BookingService } from 'src/app/services/booking.service';
import { Lab } from 'src/app/interfaces/lab';
import { Kit } from 'src/app/interfaces/kit';
import { Booking } from 'src/app/interfaces/booking';

@Component({
  selector: 'app-booking-stepper',
  templateUrl: './booking-stepper.component.html',
  styleUrls: ['./booking-stepper.component.css'],
})
export class BookingStepperComponent implements OnInit, ComponentCanDeactivate {
  @ViewChild('cd', { static: false }) private countdown!: CountdownComponent;
  @ViewChild('stepper', { read: MatStepper }) private stepper!: MatStepper;

  @HostListener('window:unload', ['$event'])
  unloadHandler(event: any) {
    this.undoReservation();
  }

  @HostListener('window:beforeunload', ['$event'])
  beforeUnloadHander(event: any) {
    if (this.bookingId !== 0) return false;

    return true;
  }

  reservationFormGroup!: FormGroup;
  confirmationFormGroup!: FormGroup;

  cols: number;
  bookingId: number = 0;

  startAt = new Date();
  minDate = new Date();
  maxDate = new Date(new Date().setMonth(new Date().getMonth() + 5));

  dateFormat: string = 'MM/DD/YYYY';
  dateTimeFormat: string = 'MMMM Do YYYY, h:mm a';
  hourFormat: string = 'hh:mm a';

  stepperOrientation: Observable<StepperOrientation>;

  labs: Lab[] = [];
  kits: Kit[] = [];
  availableHoursBySelectedDate: AvailableDate[] = [];

  isEditable: boolean = true;
  noAvailableData: boolean = false;
  restartSelectedHour: boolean = false;
  showSpinner: boolean = true;
  publicReservation: boolean = false;
  confirmedReservation: boolean = false;

  privateAccessUrl!: string;
  publicAccessUrl!: string;
  reservationDate: string = '';

  timerConfig = {
    leftTime: 420,
    format: 'mm:ss',
  };

  canDeactivate(): Observable<boolean> | boolean {
    if (this.bookingId != 0) {
      let confirmUndoReservation = confirm(
        'WARNING: You have unsaved changes. Press Cancel to go back and save these changes, or OK to lose these changes.'
      );

      if (!confirmUndoReservation) return false;
      else this.undoReservation();
    }

    return true;
  }

  constructor(
    private formBuilder: FormBuilder,
    private labService: LabService,
    private kitService: KitService,
    private bookingService: BookingService,
    private toastService: ToastrService,
    breakpointObserver: BreakpointObserver
  ) {
    this.cols = window.innerWidth <= 900 ? 1 : 2;

    this.stepperOrientation = breakpointObserver
      .observe('(min-width: 800px)')
      .pipe(map(({ matches }) => (matches ? 'horizontal' : 'vertical')));
  }

  ngOnInit() {
    this.setFormValidation();

    this.labService.getLabs().subscribe((labs) => {
      this.labs = labs;
      this.selectFirstAvailableLab();
    });
  }

  ngAfterViewInit() {
    this.initializeCountdown();
  }

  handleSize(event: any) {
    this.cols = event.target.innerWidth <= 900 ? 1 : 2;
  }

  initializeCountdown(): void {
    this.countdown.stop();
  }

  setFormValidation(): void {
    this.reservationFormGroup = this.formBuilder.group({
      selectedLab: ['', Validators.required],
      selectedKit: ['', Validators.required],
      selectedHour: ['', Validators.required],
      selectedDate: [this.startAt, Validators.required],
    });
  }

  get selectedKit(): Kit {
    return this.reservationFormGroup.controls['selectedKit'].value;
  }

  get selectedLab(): Lab {
    return this.reservationFormGroup.controls['selectedLab'].value;
  }

  get selectedDate(): Date {
    return this.reservationFormGroup.controls['selectedDate'].value;
  }

  selectFirstAvailableLab(): void {
    if (this.labs.length > 0) {
      const selectedLab = this.labs[0];

      this.reservationFormGroup.controls['selectedLab'].setValue(selectedLab);

      this.getKitsByLabId(selectedLab.id!);
    }
  }

  getKitsByLabId(labId: number): void {
    this.kitService.getKitsByLabId(labId).subscribe((kits) => {
      this.kits = kits.reverse();

      this.setDataFromFirstAvailableKit();
    });
  }

  setDataFromFirstAvailableKit(): void {
    if (this.kits.length > 0) {
      this.noAvailableData = false;

      const selectedKit = this.kits[0];

      this.reservationFormGroup.controls['selectedKit'].setValue(selectedKit);
      this.getHoursByKitIdAndDate(selectedKit.id, this.selectedDate);
    } else {
      this.noAvailableData = true;
    }
  }

  getHoursByKitIdAndDate(kitId: number, selectedDate: Date): void {
    this.showSpinner = true;
    let availableDates: AvailableDate[] = [];
    this.bookingService
      .getBookingListByKitId(kitId)
      .subscribe((bookingList) => {
        bookingList.forEach((booking) => {
          if (
            booking.available &&
            this.isAvailableDateValid(booking.start_date)
          ) {
            let formattedDate = this.getFormattedDate(
              booking.start_date,
              this.dateFormat
            );
            let formattedHour = this.getFormattedDate(
              booking.start_date,
              this.hourFormat
            );

            let availableDate = {
              formattedDate: formattedDate,
              hour: {
                bookingId: booking.id,
                formattedHour: formattedHour,
              },
            };
            availableDates.push(availableDate);
          }
        });

        let formattedSelectedDate = this.getFormattedDate(
          selectedDate,
          this.dateFormat
        );

        this.availableHoursBySelectedDate = availableDates.filter(
          (availableDate) =>
            availableDate.formattedDate == formattedSelectedDate
        );
        this.showSpinner = false;
      });
  }

  isAvailableDateValid(date: string | undefined): boolean {
    return date !== null && moment(date).isAfter(moment());
  }

  getFormattedDate(date: string | undefined | Date, format: string): any {
    return moment(date).format(format);
  }

  updateSelectedHour(bookingId: number): void {
    this.reservationFormGroup.controls['selectedHour'].setValue(bookingId);
  }

  onSelectDate(event: any): void {
    this.reservationFormGroup.controls['selectedDate'].setValue(event);
    let kit = this.reservationFormGroup.controls['selectedKit'].value;
    this.getHoursByKitIdAndDate(kit.id, event);
  }

  followNextStep() {
    this.bookingId = this.reservationFormGroup.controls['selectedHour'].value;
    this.saveReservation();
  }

  updateReservationType(publicReservation: any): void {
    this.publicReservation = publicReservation;
  }

  saveReservation(): void {
    let booking: Booking = {
      id: this.bookingId,
      available: false,
      public: this.publicReservation,
    };

    if (!this.confirmedReservation) {
      this.countdown.restart();
    }

    this.bookingService.registerBooking(booking).subscribe((updatedBooking) => {
      this.privateAccessUrl = `${config.remoteLabUrl}${updatedBooking.access_id}`;
      this.publicAccessUrl = this.publicReservation
        ? `${this.privateAccessUrl}?pwd=${updatedBooking.password}`
        : '';
      this.reservationDate = moment(updatedBooking.start_date).format(
        this.dateTimeFormat
      );
    });
  }

  undoReservation(): void {
    if (this.bookingId !== 0) {
      let booking: Booking = {
        id: this.bookingId,
        available: true,
        public: false,
        reserved_by: null,
      };

      this.bookingService.updateBooking(booking).subscribe((_) => {
        this.privateAccessUrl = '';
        this.publicAccessUrl = '';
        this.reservationDate = '';
      });

      this.countdown.restart();
      this.countdown.stop();
    }
  }

  confirmReservation(): void {
    this.isEditable = false;
    this.confirmedReservation = true;

    this.saveReservation();

    if (this.privateAccessUrl !== '') {
      this.toastService.success('Reservation made successfully');

      this.countdown.stop();

      this.resetBookingId();
    }
  }

  handleEvent(e: CountdownEvent) {
    if (e.action == 'done') {
      this.resetStepper();
      this.toastService.error(
        'The remaining time to make a reservation has ended'
      );
    }
  }

  resetStepper(): void {
    this.countdown.restart();
    this.countdown.stop();

    this.stepper.reset();

    if (this.bookingId !== 0) {
      this.undoReservation();
      this.resetBookingId();
    }

    this.selectFirstAvailableLab();
  }

  onStepChange(event: any) {
    if (event.selectedIndex == 0 && event.previouslySelectedIndex == 1) {
      this.undoReservation();
    }
  }

  resetBookingId(): void {
    this.bookingId = 0;
  }

  resetSelectedHour(): void {
    this.reservationFormGroup.controls['selectedHour'].reset();
  }
}
