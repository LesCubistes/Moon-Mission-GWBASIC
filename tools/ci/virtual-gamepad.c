/* Test-only SDL 1.2 joystick shim for DOSBox's emulated PC gameport.
 * No kernel devices are created and no desktop/controller configuration changes.
 * MOON_TEST_JOYSTICK contains signed X Y and a four-button bit mask.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef struct SDL_Joystick SDL_Joystick;
static int handle;
static void state(int *x, int *y, int *buttons) {
    *x = *y = *buttons = 0;
    const char *path = getenv("MOON_TEST_JOYSTICK");
    FILE *f = path ? fopen(path, "r") : NULL;
    if (f) { if (fscanf(f, "%d %d %d", x, y, buttons) != 3) *x = *y = *buttons = 0; fclose(f); }
}
int SDL_NumJoysticks(void) { return 1; }
const char *SDL_JoystickName(int index) { (void)index; return "Moon Mission test gameport"; }
SDL_Joystick *SDL_JoystickOpen(int index) { return index == 0 ? (SDL_Joystick *)&handle : NULL; }
int SDL_JoystickOpened(int index) { return index == 0; }
int SDL_JoystickIndex(SDL_Joystick *j) { (void)j; return 0; }
int SDL_JoystickNumAxes(SDL_Joystick *j) { (void)j; return 4; }
int SDL_JoystickNumButtons(SDL_Joystick *j) { (void)j; return 4; }
int SDL_JoystickNumHats(SDL_Joystick *j) { (void)j; return 0; }
int SDL_JoystickNumBalls(SDL_Joystick *j) { (void)j; return 0; }
int16_t SDL_JoystickGetAxis(SDL_Joystick *j, int axis) { int x,y,b; (void)j; state(&x,&y,&b); return axis == 0 ? x : axis == 1 ? y : 0; }
uint8_t SDL_JoystickGetButton(SDL_Joystick *j, int button) { int x,y,b; (void)j; state(&x,&y,&b); return button >= 0 && button < 4 ? !!(b & (1 << button)) : 0; }
void SDL_JoystickUpdate(void) {}
int SDL_JoystickEventState(int enabled) { (void)enabled; return 0; }
void SDL_JoystickClose(SDL_Joystick *j) { (void)j; }
