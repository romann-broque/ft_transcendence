import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { RouterLink } from '@angular/router';
import {FormsModule} from "@angular/forms";

@Component({
  selector: 'app-online-game-selector-page',
  standalone: true,
  imports: [
    HeaderComponent,
    RouterLink,
    FormsModule,
  ],
  templateUrl: './online-game-selector-page.component.html',
  styleUrl: './online-game-selector-page.component.css'
})

export class OnlineGameSelectorPageComponent {
  gameID: string | null = null;

  constructor() {}


}
