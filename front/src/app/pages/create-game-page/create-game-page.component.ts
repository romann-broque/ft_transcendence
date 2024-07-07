import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { SliderComponent } from '../../components/slider/slider.component';
import * as Constants from '../../constants';
import {ActivatedRoute, RouterLink} from '@angular/router';
import { EventEmitter } from '@angular/core';
import { Router, NavigationExtras } from '@angular/router';
import { NgIf } from "@angular/common";
import { UserService } from "../../services/user/user.service";

@Component({
  selector: 'app-create-game-page',
  standalone: true,
  imports: [
    HeaderComponent,
    SliderComponent,
    RouterLink,
    NgIf,
  ],
  templateUrl: './create-game-page.component.html',
  styleUrl: './create-game-page.component.css'
})
export class CreateGamePageComponent {
  constants = Constants;
  isRemote = false;
  urlDestination = '/';
  initialSettings: number[] = this._gameSettingsFromBackend;
  options: Option[] = [
    new Option('ballSpeed', this.constants.BALL_SPEED_OPTIONS, this.initialSettings[this.constants.BALL_SPEED]),
    new Option('paddleSize', this.constants.PADDLE_SIZE_OPTIONS, this.initialSettings[this.constants.PADDLE_SIZE]),
    new Option('numberPlayers', this.constants.NUMBER_PLAYERS_OPTIONS, this.initialSettings[this.constants.NUMBER_PLAYERS]),
    new Option('isPrivate', this.constants.IS_PRIVATE_OPTIONS, this.initialSettings[this.constants.IS_PRIVATE]),
  ];
  saveConfig: boolean = false;
  settingsSaved: number[] = [];

  constructor(private router: Router, private route: ActivatedRoute, private userService: UserService) {
    const gameType = this.route.snapshot.data['gameType'];
    this.isRemote = (gameType === 'online');
    if (this.isRemote) {
      this.urlDestination = '/online/create/waiting';
    } else {
      this.urlDestination = '/local/waiting';
    }
  }

  public handleOptionSelected(optionIndex: number, optionType: number): void {
    this.options[optionType].optionIndex = optionIndex;

    if (this._isBadSelection() && optionType === this.constants.PADDLE_SIZE) {
      this.options[this.constants.BALL_SPEED].optionIndex = 4;
    }
  }

  private _isBadSelection(): boolean {
    return false;
    // return (this.options[this.constants.BALL_SPEED].value() === 'snail' && this.options[this.constants.PADDLE_SIZE].value() === 'jumbo');
  }

  get _gameSettingsFromBackend(): number[] {
    if (!this.userService) {
      console.error('User service not found');
      return [];
    }
    console.log('Settings from backend: ', this.userService.getGameSettings());
    return this.userService.getGameSettings();
  }

  public saveSettings(event: Event): void {
    const inputElement = event.target as HTMLInputElement;
    const save: boolean = inputElement.checked;
    if (save) {
        this.saveConfig = true;
    }
    else {
      this.saveConfig = false;
    }
  }

  private _setSavedSettings(): void {
    this.settingsSaved = [
      this.options[this.constants.BALL_SPEED].optionIndex, 
      this.options[this.constants.PADDLE_SIZE].optionIndex, 
      this.options[this.constants.NUMBER_PLAYERS].optionIndex,
      this.options[this.constants.IS_PRIVATE].optionIndex,
    ]
  }

  private _sendSettingsToBackend(): void {
    this._setSavedSettings();
    this.userService.setGameSettings(this.settingsSaved);
  }

  private _getSelectedOptions(): number[] {
    const selectedOptions = [
      this.options[this.constants.BALL_SPEED].value(),
      this.options[this.constants.PADDLE_SIZE].value(),
      this.options[this.constants.NUMBER_PLAYERS].value(),
      this.options[this.constants.IS_PRIVATE].value()
    ];
    if (this.isRemote)
      selectedOptions.pop();
    return selectedOptions;
  }

  public navigateToWaitPage(): void {
    console.log('Navigating to join game');
    const selectedOptions = this._getSelectedOptions();
    if (this.saveConfig)
      this._sendSettingsToBackend();
    const navigationExtras: NavigationExtras = {
      state: {
        options: selectedOptions
      }
    };
    this.router.navigate([this.urlDestination], navigationExtras);
  }
}

export class Option {
  optionIndexChange = new EventEmitter<number>();

  constructor(public name: string, public options: string[], private _optionIndex: number) {}

  public get optionIndex(): number {
    return this._optionIndex;
  }

  public set optionIndex(optionIndex: number) {
    this._optionIndex = optionIndex;
    this.optionIndexChange.emit(this._optionIndex);
  }

  public value(): number {
    return this._optionIndex;
  }
}
