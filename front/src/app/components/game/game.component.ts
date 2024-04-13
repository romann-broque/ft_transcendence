import {AfterViewInit, Component, HostListener, QueryList, ViewChildren} from '@angular/core';
import {GAME_HEIGHT, GAME_WIDTH, LINE_THICKNESS, PADDLE_HEIGHT, PADDLE_WIDTH} from "../../constants";
import {PaddleComponent} from "../paddle/paddle.component";
import {BallComponent} from "../ball/ball.component";
import {WebSocketService} from "../../services/web-socket/web-socket.service";
import {MonitorService} from "../../services/monitor/monitor.service";

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [
    PaddleComponent,
    BallComponent
  ],
  templateUrl: './game.component.html',
  styleUrl: './game.component.css'
})
export class GameComponent implements AfterViewInit {
  player1Score = 0;
  player2Score = 0;
  readonly gameWidth = GAME_WIDTH;
  readonly gameHeight = GAME_HEIGHT;
  lineThickness = LINE_THICKNESS;
  @ViewChildren(PaddleComponent) paddles!: QueryList<PaddleComponent>;
  @ViewChildren(BallComponent) ball!: QueryList<BallComponent>;
  postData = JSON.stringify({"playerSpecs":
     {"nbPlayers": 2, "mode": 0}
  })
  private paddleBinding = [
    { id: 1, upKey: 'w', downKey: 's' },
    { id: 2, upKey: 'ArrowUp', downKey: 'ArrowDown' },
  ];

  private pressedKeys = new Set<string>();

  constructor(private monitorService: MonitorService, private webSocketService: WebSocketService) {
    this.establishConnection();
  }

  @HostListener('window:keydown', ['$event'])
  private onKeyDown(event: KeyboardEvent) {
    this.pressedKeys.add(event.key);
  }

  @HostListener('window:keyup', ['$event'])
  private onKeyUp(event: KeyboardEvent) {
    this.pressedKeys.delete(event.key);
  }

  private establishConnection() {
    this.monitorService.getWebSocketUrl(this.postData).subscribe(response => {
      console.log(response)
      this.webSocketService.connect(response.channelID)
      this.webSocketService.getConnectionOpenedEvent().subscribe(() => {
        console.log('WebSocket connection opened');
        this.webSocketService.join(response.arenaID)
      })
    });
  }

  public endConnection() {
    console.log('WebSocket connection closed');
    this.webSocketService.disconnect();
  }

  private gameLoop() {
    this.paddleBinding.forEach(paddleBinding => {
      const paddle = this.paddles.find(p => p.id === paddleBinding.id);
      if (paddle) {
        this.movePaddle(paddle, paddleBinding)
      }
    });

    // Call this function again on the next frame
    requestAnimationFrame(() => this.gameLoop());
  }

  private movePaddle(paddle: PaddleComponent, binding: { upKey: string; downKey: string }) {
    const isMovingUp = this.pressedKeys.has(binding.upKey) && !this.pressedKeys.has(binding.downKey);
    const isMovingDown = this.pressedKeys.has(binding.downKey) && !this.pressedKeys.has(binding.upKey);

    if (isMovingUp) {
      paddle.moveUp();
      this.webSocketService.sendPaddleMovement(paddle.id, paddle.positionY);
    } else if (isMovingDown) {
      paddle.moveDown();
      this.webSocketService.sendPaddleMovement(paddle.id, paddle.positionY);
    }
  }

  ngAfterViewInit() {
    this.gameLoop();
  }

  protected readonly PADDLE_WIDTH = PADDLE_WIDTH;
  protected readonly PADDLE_HEIGHT = PADDLE_HEIGHT;
}
