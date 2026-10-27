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
    static int last_x = -99999, last_y = -99999, last_buttons = -1;
    if (*x != last_x || *y != last_y || *buttons != last_buttons) {
        fprintf(stderr, "TEST GAMEPORT x=%d y=%d buttons=%d\n", *x,*y,*buttons);
        last_x=*x; last_y=*y; last_buttons=*buttons;
    }
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

/* DOSBox consumes joystick motion/button events after opening the device. */
#include <string.h>
#include <dlfcn.h>
typedef union {
    uint8_t type;
    struct { uint8_t type, which, axis, padding; int16_t value; } axis;
    struct { uint8_t type, which, button, state; } button;
    uint8_t padding[24];
} TestEvent;
int SDL_PollEvent(void *event) {
    static int (*real_poll)(void *) = NULL;
    static int old_x, old_y, old_buttons;
    int x,y,buttons;
    if (!real_poll) real_poll = (int (*)(void *))dlsym(RTLD_NEXT, "SDL_PollEvent");
    if (real_poll && real_poll(event)) return 1;
    if (!event) return 0;
    state(&x,&y,&buttons);
    TestEvent next; memset(&next,0,sizeof(next));
    if (x != old_x || y != old_y) {
        next.axis.type = 7;
        if (x != old_x) { next.axis.axis = 0; next.axis.value = x; old_x = x; }
        else { next.axis.axis = 1; next.axis.value = y; old_y = y; }
    } else {
        int changed = buttons ^ old_buttons;
        if (!changed) return 0;
        int button = 0;
        while (!(changed & (1 << button))) ++button;
        int pressed = !!(buttons & (1 << button));
        next.button.type = pressed ? 10 : 11;
        next.button.button = button;
        next.button.state = pressed;
        old_buttons ^= 1 << button;
    }
    memcpy(event,&next,sizeof(next));
    return 1;
}
