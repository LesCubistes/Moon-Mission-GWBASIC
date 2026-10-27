10 REM ==== MOON MISSION - START disk: title screen, high scores, mission menu ====
20 REM Needs MOONBG.PIC, EARTH.SPR, TITLE.SPR, CREDIT.SPR, ROLL.BIN, ROLL.DAT here; each mission lives on its own disk in drive B:
25 COMMON SK%, LS%, LD$
26 COMMON JE%, JX%, JY%, JH%, JV%, JB%, JQ!, JM%
30 DEFINT A-Z: KEY OFF: CLS
40 EX = 112: EY = 33: HT = 126: SH = 82
50 Y = 0: K = 0: S = 1: NM = 2: MI = 1: NMU = 0: A$ = "": DT! = .2: T0! = 0: KP = 0: HR = 0: HE = 0: I = 0: LD$ = "B:": P$ = "": TY = 0
52 DEF SEG = &H40: I = PEEK(&H10): DEF SEG: IF (I AND &HC1) = 1 THEN LD$ = "A:": REM only one floppy drive: the mission disk goes in A: too
53 DEF SEG = &HF000: TY = (PEEK(49152!) = &H21): DEF SEG: REM a Tandy 1000 needs its own palette registers set
55 TS = 0: TW! = 0: TK = 0: NT = 0: SS = 0: SN! = 0: SPX = 0: SPY = 0: SDX = 0: J = 0: RS = 0: RA! = 0: RT! = 0: RN = 0
57 JE% = JE%: JX% = JX%: JY% = JY%: JH% = JH%: JV% = JV%: JB% = JB%: JQ! = 0: JM% = JM%
58 JF% = 0: JA$ = "": JC% = 0: JD% = 0: JL% = 0: JU% = 0: JR% = 0: JW% = 0: JT% = 0: JK% = 0: JZ% = 0: JI% = 0
60 DIM E(986), T(681), CR(376), M$(2), MU$(12), HB(4100), HN$(10), HS!(10), HL$(10)
65 DIM TX(16), TY(16), TC(16), QX(3), QY(3), QC(3), PR(11), RC(249)
70 M$(1) = "MOON LANDING": M$(2) = "EXIT TO DOS"
80 GOSUB 5000
85 RESTORE 9600: READ NT: FOR I = 1 TO NT: READ TX(I), TY(I), TC(I): NEXT I: QX(1) = -1: QX(2) = -1: QX(3) = -1: SN! = TIMER + 5
90 REM ---- rolling moonscape: 64K from DOS for the ground (ROLL.DAT); without it the Moon stands still ----
92 PR(0) = 0: RA! = VARPTR(RC(0)): BLOAD "ROLL.BIN", RA!: CALL RA!(PR(0)): RS = PR(1): IF RS THEN DEF SEG = RS: BLOAD "ROLL.DAT", 0: DEF SEG
100 REM ---- load art with the display switched off ----
110 SCREEN 1, 0: COLOR 0, 1: CLS
120 OUT &H3D8, &H6
130 DEF SEG = &HB800: BLOAD "MOONBG.PIC", 0: DEF SEG
140 BLOAD "EARTH.SPR", VARPTR(E(0))
150 BLOAD "TITLE.SPR", VARPTR(T(0))
155 BLOAD "CREDIT.SPR", VARPTR(CR(0))
170 PR(3) = -1: PR(7) = -1: PR(10) = -1: GOSUB 8950
180 IF SK% = 1 THEN MI = NMU + 1: GOTO 400
200 REM ---- earthrise: draw only the rows above the horizon (with the rolling ground, ROLL.BIN draws it) ----
205 IF INKEY$ <> "" THEN 205: REM ignore keys pressed while the art was loading
210 GOSUB 900
220 T0! = TIMER
230 FOR K = 1 TO HT - EY
240 Y = HT - K
250 IF K < SH THEN E(1) = K ELSE E(1) = SH
255 IF RS THEN PR(10) = Y ELSE PUT (EX, Y), E, PSET
260 GOSUB 900: GOSUB 950: GOSUB 940
270 IF INKEY$ <> "" THEN KP = 1: GOTO 400
280 IF TIMER < T0! + K * DT! THEN GOTO 260
290 NEXT K
400 REM ---- title; once the music ends show high scores; then the menu ----
405 PR(10) = -1: GOSUB 990
410 LINE (EX, EY)-(EX + 95, HT - 1), 0, BF: E(1) = SH: PUT (EX, EY), E, PSET
420 PUT (24, 6), T, PSET: PUT (216, 34), CR, PSET: REM "by Ryan Barrineau" under the title
425 IF SK% <> 1 AND KP = 0 THEN GOSUB 1000
430 PR(2) = 146: PR(3) = 197: PR(4) = 18: PR(5) = 62: PR(6) = 176: PR(7) = 199: PR(8) = 0: PR(9) = 16: LINE (72, 146)-(247, 197), 0, BF: LINE (72, 146)-(247, 197), 1, B
440 LOCATE 20, 12: PRINT "- SELECT MISSION -";
450 FOR K = 1 TO NM: LOCATE 20 + 2 * K, 15: PRINT M$(K);: NEXT K
460 GOSUB 600
465 GOSUB 6900
470 GOSUB 900: GOSUB 950: GOSUB 940: A$ = INKEY$
472 IF A$ = "" AND JE% THEN JF% = 0: GOSUB 6800: A$ = JA$
474 IF A$ = "" THEN 470
476 IF A$ = "j" OR A$ = "J" THEN GOSUB 6500: SK% = 1: GOTO 100
478 IF A$ = "k" OR A$ = "K" THEN JE% = 0: STRIG OFF: GOSUB 6900: GOTO 470
480 IF A$ = CHR$(0) + "H" AND S > 1 THEN S = S - 1: GOSUB 600
490 IF A$ = CHR$(0) + "P" AND S < NM THEN S = S + 1: GOSUB 600
500 IF A$ >= "1" AND A$ <= CHR$(48 + NM) THEN S = ASC(A$) - 48: GOSUB 600: A$ = CHR$(13)
510 IF A$ = CHR$(27) THEN S = NM: A$ = CHR$(13)
520 IF A$ <> CHR$(13) THEN 470
530 ON S GOTO 700, 800
600 REM ---- draw selection box ----
610 FOR K = 1 TO NM
620 LINE (108, 150 + 16 * K)-(211, 161 + 16 * K), -2 * (K = S), B
630 NEXT K: RETURN
700 REM ---- moon landing: load the level from the LUNAR LANDING disk (drive B:, or A: when there is only one drive) ----
705 IF LD$ = "A:" THEN P$ = "INSERT THE LUNAR LANDING DISK": GOSUB 780: IF A$ = CHR$(27) THEN 470
710 GOSUB 945: ON ERROR GOTO 750: CHAIN LD$ + "LANDER"
750 RESUME 755
755 ON ERROR GOTO 0: P$ = "LUNAR LANDING DISK NOT FOUND": GOSUB 780: IF A$ = CHR$(27) THEN 470 ELSE 710
780 GET (16, 60)-(303, 107), HB: LINE (16, 60)-(303, 107), 0, BF: LINE (16, 60)-(303, 107), 2, B: LOCATE 10, 21 - LEN(P$) \ 2: PRINT P$;
782 LOCATE 12, 7: PRINT "IN DRIVE "; LD$; " AND PRESS A KEY";: LOCATE 13, 14: PRINT "(ESC = CANCEL)";
785 SOUND 200, 3: A$ = INKEY$: IF A$ <> "" THEN 785
790 GOSUB 900: GOSUB 940: A$ = INKEY$
791 IF A$ = "" AND JE% THEN JF% = 0: GOSUB 6800: A$ = JA$
792 IF A$ = "" THEN 790
795 PUT (16, 60), HB, PSET: RETURN
800 REM ---- exit ----
810 GOSUB 945: SCREEN 0, 0: WIDTH 80: SYSTEM
900 REM ---- feed music a few notes at a time so PLAY never blocks ----
910 IF MI <= NMU THEN IF PLAY(0) < 4 THEN PLAY MU$(MI): MI = MI + 1
920 RETURN
940 IF RS = 0 OR TIMER = RT! THEN RETURN ELSE RN = 1: IF TIMER > RT! AND TIMER < RT! + .35 THEN RN = INT((TIMER - RT!) * 18.2 + .5)
942 RT! = TIMER: PR(0) = 1: PR(1) = RS: PR(11) = RN: RA! = VARPTR(RC(0)): CALL RA!(PR(0)): RETURN: REM the ground rolls one step per clock tick
945 IF RS THEN PR(0) = 3: PR(1) = RS: RA! = VARPTR(RC(0)): CALL RA!(PR(0)): RS = 0: REM give the 64K back before CHAIN or SYSTEM
946 RETURN
950 REM ---- life on the title: stars twinkle, now and then a shooting star streaks past ----
952 IF TIMER < TW! THEN RETURN
954 TW! = TIMER + .06: IF SS THEN GOSUB 970 ELSE IF TIMER > SN! THEN GOSUB 965
956 TK = TK + 1: IF TK MOD 4 THEN RETURN
958 IF TS THEN PSET (TX(TS), TY(TS)), TC(TS)
960 TS = INT(RND * NT) + 1: IF RND < .6 THEN PSET (TX(TS), TY(TS)), 0 ELSE TS = 0
962 RETURN
965 SS = 1: SPY = 40 + INT(RND * 20): IF RND < .5 THEN SPX = 60 + INT(RND * 30): SDX = -4 ELSE SPX = 224 + INT(RND * 30): SDX = 4
966 RETURN
970 IF QX(3) >= 0 THEN LINE (QX(3), QY(3))-(QX(3) - SDX, QY(3) - 2), 0
972 QX(3) = QX(2): QY(3) = QY(2): QX(2) = QX(1): QY(2) = QY(1): IF QX(2) >= 0 THEN LINE (QX(2), QY(2))-(QX(2) - SDX, QY(2) - 2), 1
974 IF SS > 14 THEN QX(1) = -1: IF QX(3) < 0 THEN SS = 0: SN! = TIMER + 5 + RND * 8: RETURN ELSE RETURN
976 SPX = SPX + SDX: SPY = SPY + 2: QX(1) = SPX: QY(1) = SPY: LINE (SPX, SPY)-(SPX - SDX, SPY - 2), 3: SS = SS + 1: RETURN
990 REM ---- put back any star or shooting-star pixels before the screen changes ----
992 FOR J = 3 TO 1 STEP -1: IF QX(J) >= 0 THEN LINE (QX(J), QY(J))-(QX(J) - SDX, QY(J) - 2), 0: QX(J) = -1
994 NEXT J: IF TS THEN PSET (TX(TS), TY(TS)), TC(TS): TS = 0
996 SS = 0: SN! = TIMER + 6: RETURN
1000 REM ---- attract: wait for the music to finish, show high scores ~6 s ----
1010 GOSUB 900: GOSUB 950: GOSUB 940: IF INKEY$ <> "" THEN RETURN
1020 IF MI <= NMU OR PLAY(0) > 0 THEN 1010
1030 T0! = TIMER + 1
1035 IF INKEY$ <> "" THEN RETURN ELSE IF TIMER < T0! THEN 1035
1040 GOSUB 990: GET (32, 44)-(287, 171), HB: GOSUB 8100: HR = 0: GOSUB 8500
1050 LOCATE 20, 14: PRINT "PRESS ANY KEY";: T0! = TIMER + 6
1060 IF INKEY$ = "" AND TIMER < T0! THEN 1060
1070 PUT (32, 44), HB, PSET: RETURN
5000 REM ---- Also sprach Zarathustra (opening) ----
5010 FOR K = 1 TO 9: READ MU$(K): NEXT K: NMU = 9: RETURN
5020 DATA "MBT100O1C1O3L4C2G2", "O4C2.E16E-1"
5030 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5040 DATA "O3L4C2G2O4C2.E-16E1"
5050 DATA "O2L8CO1GO2CO1G", "O2CO1GO2CO1GO2C4"
5060 DATA "O3L4C2G2O4C2.", "A1B4O5C1."
6500 REM ---- opt-in Gravis/standard gameport calibration; no reads while keyboard-only ----
6505 JE% = 0: STRIG ON: SCREEN 0, 0: WIDTH 40: COLOR 7, 0: CLS
6510 PRINT "GAMEPORT GAMEPAD SETUP": PRINT: PRINT "Use the standard 2/4-button mode.": PRINT "Keyboard ESC cancels setup.": PRINT
6515 PRINT "Release the direction pad.": PRINT "Press ENTER to sample center."
6520 GOSUB 6760: IF JA$ = CHR$(27) THEN 6740
6525 JX% = STICK(0): JY% = STICK(1)
6530 PRINT "Hold UP-LEFT; press ENTER."
6535 GOSUB 6760: IF JA$ = CHR$(27) THEN 6740
6540 JL% = STICK(0): JU% = STICK(1)
6545 PRINT "Hold DOWN-RIGHT; press ENTER."
6550 GOSUB 6760: IF JA$ = CHR$(27) THEN 6740
6555 JR% = STICK(0): JW% = STICK(1)
6560 IF JX% <= 0 OR JY% <= 0 OR JL% >= JX% OR JR% <= JX% OR JU% >= JY% OR JW% <= JY% THEN 6720
6565 JH% = (JR% - JL%) \ 4: JV% = (JW% - JU%) \ 4
6570 IF JH% < 2 OR JV% < 2 THEN 6720
6575 IF JX% - JL% <= JH% OR JR% - JX% <= JH% OR JY% - JU% <= JV% OR JW% - JY% <= JV% THEN 6720
6580 JE% = 1: JB% = 15: JQ! = 0: PRINT: PRINT "GAMEPAD ENABLED"
6585 PRINT "Red A: confirm / throttle up": PRINT "Blue B: back / throttle down"
6590 PRINT "Yellow C: engine off": PRINT "Green D: back to orbit/menu"
6595 PRINT "D-pad: menus / flight keypad": PRINT
6596 PRINT "Hold A to burn? (Y/N)": PRINT " Y: engine runs only while A is held,": PRINT "    D-pad up/down sets the power": PRINT " N: each A press adds 10% power"
6597 JA$ = INKEY$: IF JA$ <> "" THEN 6597
6598 JA$ = INKEY$: IF JA$ = "" OR INSTR("YyNn", JA$) = 0 THEN 6598
6599 JM% = -(JA$ = "Y" OR JA$ = "y"): IF JM% THEN PRINT "HOLD A TO BURN: ON" ELSE PRINT "HOLD A TO BURN: OFF"
6600 PRINT "Release pad; ENTER to return.": GOSUB 6760: RETURN
6720 PRINT: PRINT "No usable calibrated gameport found.": PRINT "Check port, pad mode and directions."
6721 PRINT "CENTER "; JX%; JY%: PRINT "UP-LEFT "; JL%; JU%: PRINT "DOWN-RIGHT "; JR%; JW%
6722 PRINT "Keyboard controls remain active.": PRINT "Press ENTER."
6725 GOSUB 6760
6740 JE% = 0: STRIG OFF: RETURN
6760 JA$ = INKEY$: IF JA$ <> "" THEN 6760
6765 JA$ = INKEY$: IF JA$ <> CHR$(13) AND JA$ <> CHR$(27) THEN 6765
6770 RETURN
6800 REM ---- optional gameport: STICK(0) refreshes axes; menu buttons use rising edges ----
6805 JA$ = "": IF JE% = 0 THEN RETURN
6810 IF TIMER < JQ! THEN IF JQ! - TIMER < 1 THEN RETURN
6815 JQ! = TIMER + .15: JC% = STICK(0): JD% = STICK(1)
6820 REM zero is a valid full-travel axis reading; K always restores keyboard-only input
6825 JZ% = 0: IF STRIG(1) THEN JZ% = JZ% OR 1
6830 IF STRIG(5) THEN JZ% = JZ% OR 2
6835 IF STRIG(3) THEN JZ% = JZ% OR 4
6840 IF STRIG(7) THEN JZ% = JZ% OR 8
6845 JI% = JZ% AND NOT JB%: JB% = JZ%: IF JF% THEN JI% = JZ%
6850 IF JI% AND 8 THEN JA$ = CHR$(27): RETURN
6855 IF JI% AND 4 THEN JA$ = " ": RETURN
6860 IF JI% AND 2 THEN IF JF% THEN JA$ = "5": RETURN ELSE JA$ = CHR$(27): RETURN
6865 IF JI% AND 1 THEN IF JF% THEN JA$ = "8": RETURN ELSE JA$ = CHR$(13): RETURN
6870 JT% = 0: JK% = 0: IF JC% < JX% - JH% THEN JT% = -1 ELSE IF JC% > JX% + JH% THEN JT% = 1
6875 IF JD% < JY% - JV% THEN JK% = -1 ELSE IF JD% > JY% + JV% THEN JK% = 1
6880 IF JT% = 0 AND JK% = 0 THEN RETURN
6885 IF JF% THEN IF JT% = 0 AND JK% = 1 THEN JA$ = "5": RETURN ELSE JA$ = CHR$(53 + JT% - 3 * JK%): RETURN
6890 IF JK% < 0 THEN JA$ = CHR$(0) + "H": RETURN ELSE IF JK% > 0 THEN JA$ = CHR$(0) + "P": RETURN
6895 IF JT% < 0 THEN JA$ = CHR$(0) + "K" ELSE JA$ = CHR$(0) + "M"
6898 RETURN
6900 LINE (0, 176)-(63, 199), 0, BF: LOCATE 23, 1: PRINT "J=PAD";: LOCATE 24, 1: PRINT "K=KEYS";: LOCATE 25, 1: IF JE% = 0 THEN PRINT "PAD OFF"; ELSE IF JM% THEN PRINT "PAD HOLD"; ELSE PRINT "PAD ON";
6905 RETURN
8100 REM ---- load the high score table (empty until the first scores are saved in LANDHS.DAT) ----
8110 HE = 0: ON ERROR GOTO 8180
8120 OPEN "LANDHS.DAT" FOR INPUT AS #1
8130 IF HE = 0 THEN FOR I = 1 TO 10: INPUT #1, HN$(I), HS!(I), HL$(I): NEXT I
8140 CLOSE #1: ON ERROR GOTO 0
8150 IF HE THEN FOR I = 1 TO 10: HN$(I) = "": HS!(I) = 0: HL$(I) = "": NEXT I
8160 RETURN
8180 HE = 1: RESUME NEXT
8500 REM ---- draw the high score table; HR = rank to highlight (0 = none) ----
8510 LINE (32, 44)-(287, 171), 0, BF: LINE (32, 44)-(287, 171), 1, B
8520 LOCATE 7, 15: PRINT "HIGH SCORES";: LINE (116, 57)-(203, 57), 1
8530 FOR I = 1 TO 10: LOCATE 8 + I, 7: IF HS!(I) > 0 THEN PRINT USING "##. \ \  ######  "; I; HN$(I); HS!(I);: PRINT HL$(I); ELSE PRINT USING "##.  ---"; I;
8535 NEXT I
8540 IF HR THEN LINE (44, 55 + 8 * HR)-(277, 64 + 8 * HR), 2, B
8550 RETURN
8940 REM ---- display on, palette cyan / red / grey (CGA: the mode register's B/W bit). A Tandy 1000 picks palette registers 3, 4, 7 for that, so open its palette mask (it masks them to 0-3) and set them ----
8950 OUT &H3D8, &HE: OUT &H3D9, 0: IF TY = 0 THEN RETURN
8952 I = INP(&H3DA): OUT &H3DA, 1: OUT &H3DE, &HF: OUT &H3DA, &H10: OUT &H3DE, 0: OUT &H3DA, &H13: OUT &H3DE, 3: OUT &H3DA, &H14: OUT &H3DE, 4: OUT &H3DA, &H17: OUT &H3DE, 7: RETURN
9590 REM ---- stars that twinkle: count, then x, y, colour (picked by tools/mkstars.py from MOONBG.PIC) ----
9600 DATA 16,10,73,3,11,81,3,28,109,3,30,58,3,44,58,3,52,70,1,71,98,3,93,119
9601 DATA 3,242,80,3,242,118,3,226,84,1,274,92,3,290,78,3,303,82,1,306,99,3,317,53
9602 DATA 3
