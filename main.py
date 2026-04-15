import random
import tkinter as tk


# Core game tuning values.
WIDTH = 600
HEIGHT = 700
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 20
PLAYER_SPEED = 18
STAR_SIZE = 20
STAR_SPEED_START = 5
SPAWN_RATE_MS = 700
GAME_TIME = 45


class StarCatcherGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Star Catcher")
        self.root.resizable(False, False)

        # Everything in the game is drawn on this canvas.
        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#0b1021",
            highlightthickness=0,
        )
        self.canvas.pack()

        # Runtime state used by the update loops.
        self.left_pressed = False
        self.right_pressed = False
        self.running = True
        self.score = 0
        self.time_left = GAME_TIME
        self.star_speed = STAR_SPEED_START
        self.stars = []

        self.draw_background()
        # The player platform is a simple rectangle near the bottom of the screen.
        self.player = self.canvas.create_rectangle(
            WIDTH // 2 - PLAYER_WIDTH // 2,
            HEIGHT - 70,
            WIDTH // 2 + PLAYER_WIDTH // 2,
            HEIGHT - 70 + PLAYER_HEIGHT,
            fill="#f4d35e",
            outline="",
        )

        self.score_text = self.canvas.create_text(
            90,
            30,
            text=f"Score: {self.score}",
            fill="white",
            font=("Segoe UI", 18, "bold"),
        )
        self.timer_text = self.canvas.create_text(
            WIDTH - 90,
            30,
            text=f"Time: {self.time_left}",
            fill="white",
            font=("Segoe UI", 18, "bold"),
        )
        self.message_text = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="Catch the stars!\nUse Left/Right arrows",
            fill="#d9e2ff",
            font=("Segoe UI", 24, "bold"),
            justify="center",
        )

        # Key press/release bindings let movement feel continuous while a key is held.
        root.bind("<KeyPress-Left>", self.on_left_press)
        root.bind("<KeyRelease-Left>", self.on_left_release)
        root.bind("<KeyPress-Right>", self.on_right_press)
        root.bind("<KeyRelease-Right>", self.on_right_release)
        root.bind("<space>", self.restart_game)

        # Small delay so the opening instructions are visible before the game starts.
        self.root.after(1500, self.start_game)

    def draw_background(self) -> None:
        # Draw a starry sky backdrop for a bit of atmosphere.
        for _ in range(55):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#bcd4ff",
                outline="",
            )

        self.canvas.create_text(
            WIDTH // 2,
            80,
            text="STAR CATCHER",
            fill="#ffffff",
            font=("Segoe UI", 28, "bold"),
        )

    def start_game(self) -> None:
        # Kick off the three repeating systems: star spawning, countdown, and frame updates.
        self.canvas.itemconfig(self.message_text, text="")
        self.schedule_spawn()
        self.tick_timer()
        self.game_loop()

    def on_left_press(self, _event) -> None:
        self.left_pressed = True

    def on_left_release(self, _event) -> None:
        self.left_pressed = False

    def on_right_press(self, _event) -> None:
        self.right_pressed = True

    def on_right_release(self, _event) -> None:
        self.right_pressed = False

    def move_player(self) -> None:
        if not self.running:
            return

        # Convert held keys into horizontal movement for this frame.
        dx = 0
        if self.left_pressed:
            dx -= PLAYER_SPEED
        if self.right_pressed:
            dx += PLAYER_SPEED

        if dx == 0:
            return

        # Clamp the platform so it stays inside the play area.
        x1, _, x2, _ = self.canvas.coords(self.player)
        if x1 + dx < 20:
            dx = 20 - x1
        if x2 + dx > WIDTH - 20:
            dx = (WIDTH - 20) - x2
        self.canvas.move(self.player, dx, 0)

    def create_star(self) -> None:
        # Spawn one falling star just above the top edge at a random x-position.
        x = random.randint(30, WIDTH - 30)
        star = self.canvas.create_oval(
            x,
            -STAR_SIZE,
            x + STAR_SIZE,
            0,
            fill=random.choice(["#ff6b6b", "#6bcBef", "#95e06c", "#ffd166", "#c792ea"]),
            outline="",
        )
        self.stars.append(star)

    def schedule_spawn(self) -> None:
        if not self.running:
            return

        self.create_star()
        # Re-schedule this method so stars keep appearing over time.
        self.root.after(SPAWN_RATE_MS, self.schedule_spawn)

    def update_stars(self) -> None:
        # Read the platform bounds once so every star can test against it.
        player_x1, player_y1, player_x2, player_y2 = self.canvas.coords(self.player)
        remaining = []

        for star in self.stars:
            # Move each existing star downward by the current fall speed.
            self.canvas.move(star, 0, self.star_speed)
            x1, y1, x2, y2 = self.canvas.coords(star)

            # Collision check: the star is "caught" when its bounding box overlaps
            # the platform's bounding box on both the x-axis and y-axis.
            caught = x2 >= player_x1 and x1 <= player_x2 and y2 >= player_y1 and y1 <= player_y2
            if caught:
                self.canvas.delete(star)
                self.score += 1
                # The game speeds up slightly with each successful catch.
                self.star_speed = min(self.star_speed + 0.15, 12)
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                continue

            # Remove stars that fall off-screen without being caught.
            if y1 > HEIGHT:
                self.canvas.delete(star)
                continue

            remaining.append(star)

        self.stars = remaining

    def tick_timer(self) -> None:
        if not self.running:
            return

        self.canvas.itemconfig(self.timer_text, text=f"Time: {self.time_left}")
        if self.time_left <= 0:
            self.end_game()
            return

        # Count down once per second until the round ends.
        self.time_left -= 1
        self.root.after(1000, self.tick_timer)

    def end_game(self) -> None:
        self.running = False
        # Clear any active stars and show the restart message.
        for star in self.stars:
            self.canvas.delete(star)
        self.stars.clear()
        self.canvas.itemconfig(
            self.message_text,
            text=f"Time's up!\nFinal score: {self.score}\nPress Space to play again",
        )

    def restart_game(self, _event=None) -> None:
        if self.running:
            return

        # Reset all gameplay state so a fresh round can start.
        self.running = True
        self.score = 0
        self.time_left = GAME_TIME
        self.star_speed = STAR_SPEED_START
        self.left_pressed = False
        self.right_pressed = False
        self.canvas.coords(
            self.player,
            WIDTH // 2 - PLAYER_WIDTH // 2,
            HEIGHT - 70,
            WIDTH // 2 + PLAYER_WIDTH // 2,
            HEIGHT - 70 + PLAYER_HEIGHT,
        )
        self.canvas.itemconfig(self.score_text, text="Score: 0")
        self.canvas.itemconfig(self.timer_text, text=f"Time: {GAME_TIME}")
        self.canvas.itemconfig(self.message_text, text="")
        self.schedule_spawn()
        self.tick_timer()
        self.game_loop()

    def game_loop(self) -> None:
        if not self.running:
            return

        # Main frame update: move the platform, update falling stars, then queue the next frame.
        self.move_player()
        self.update_stars()
        self.root.after(30, self.game_loop)


def main() -> None:
    # Standard tkinter startup: create the window, build the game, enter the event loop.
    root = tk.Tk()
    StarCatcherGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
