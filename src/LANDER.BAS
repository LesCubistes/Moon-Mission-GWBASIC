10 REM ==== MOON LANDING - phase 1: pick a site from orbit; phase 2: land the lunar module ====
20 REM Runs from the LUNAR LANDING disk (drive LD$, normally B:). Started by MOON on the START disk.
25 REM Keypad: 8/5 throttle up/down, 0 or SPACE engine off, 7 9 4 6 1 2 3 thrusters
30 COMMON SK%, LS%, LD$
31 COMMON JE%, JX%, JY%, JH%, JV%, JB%, JQ!
40 DEFINT A-Z: KEY OFF: RANDOMIZE TIMER
50 REM -- every simple variable is created here, before any VARPTR/BLOAD --
55 RP! = 0: T0! = 0: I = 0: OI = 0: Z = 0: DA = 0: XD = 0: DD = 0: CA! = 0: NS = 0: J = 0: K = 0: RO = 0: XF = 0: PN = 0: REM the cockpit replay loop's variables first: GW-BASIC finds early ones fastest
60 X! = 0: Y! = 0: VX! = 0: VY! = 0: F! = 0: A! = 0: DT! = 0: T0! = 0: T1! = 0: ST! = 0
70 HT! = 0: PT! = 0: TT! = 0: GR! = 3: AM! = 7: DV! = .8: VYS! = 4: VXS! = 2
80 FM! = 800: BU! = 25: RF! = 4
90 XI = 0: YI = 0: OX = -1: OY = 0: FL = 0: OF = 0: PF = 0: OP = 0: TH = 0: K = 0: I = 0
100 LK = 0: B = 0: P = 0: NP = 0: LV = 1: S = 1: SC = 0: W = 0: AL = 0: LF = 0: RG = 0: MN = 0: Q = 0
105 CT = 0: D = 0: CX = 0: GC = 0: PX = 0: PY = 0: PO = 0: PZ = 0: R = 0: J = 0
107 FX = 0: FY = 0: FR = 0: GX = 0: GY = 0: DW = 0: ALM = 0: WD! = 0: T2! = 0: AT! = 0: RL! = 0: LN = 0: SF = 0: TB = 0: LP = 0: HR = 0
108 HE = 0: LT! = 0: TS! = 0: BX! = 0: BV! = 0: BI = 0: BO = -1: BY = 0: ZN = 0: OZ = 0: MT! = 0: IM = 0: DU = 0: DX = 0: DY = 0: DC = 0
109 LT2 = 0: TL = 0: LF! = 0: F7! = 0: CXM = 0: MV! = 0: CM = 0: SD = 0: SXO = 0: CL = 0: F6 = 0: F3 = 0: A12! = 0: G12! = 0: BB = 0: BL! = 0: TS = 0: TW! = 0: NT = 0: TK = 0: SP = 0: NM = 0: SYO = 0: SL = 0: SH! = 0: MD! = 0
110 K$ = "": C$ = "": R$ = "": R2$ = "": M$ = "": N$ = "": PC$ = "": MP$ = ""
111 H1 = 0: H2 = 0: H3 = 0: H4 = 0: SYB = 0
112 LD$ = LD$ + "": SK% = SK%: LS% = LS%: REM create the COMMON ones too (LD$ is "" when run on its own: assets from the current drive)
113 CS = 0: RI = 0: NR = 0: AW = 0: SN = 1: SB = 0: HP = 0: LL = 0: MX = -1: P$ = "": TY = 0: QB = 0: QS = 0: QM = 0: QF = 0
114 DEF SEG = &HF000: TY = (PEEK(49152!) = &H21): DEF SEG: REM a Tandy 1000 needs its own palette registers set
115 JE% = JE%: JX% = JX%: JY% = JY%: JH% = JH%: JV% = JV%: JB% = JB%: JQ! = 0
116 JF% = 0: JA$ = "": JC% = 0: JD% = 0: JL% = 0: JU% = 0: JR% = 0: JW% = 0: JT% = 0: JK% = 0: JZ% = 0: JI% = 0
117 IF JE% THEN STRIG ON
120 DIM PR(9), RA(24), RD(24), RT(24), H(639), SP(146), MK(146), BG(146), F1(146), F2(146), F3(146)
125 DIM Q1(146), Q2(146), Q3(146), Q4(146), Q6(146), Q7(146), Q9(146)
127 DIM B2(172), FB(450), C1(172), C2(172), C3(172), C4(172), C5(172), C6(172), C7(172)
128 DIM M1(172), M2(172), M3(172), M4(172), M5(172), M6(172), M7(172), EU(6), EV(6)
130 DIM LA(4), LB(4), LM(4), RX!(9), RY!(9), SN$(3), SD$(3), SA(3), HN$(10), HS!(10), HL$(10), ZX(3), ZY(3), ZW(3), ZH(3)
131 DIM D1(115), D2(115), D3(115), D4(115), D5(115), D6(115)
132 DIM CMS(3), CMK(3), CG(3), SG(60), TX(16), TY(16), TC(16), QX(3), QY(3), QC(3), EB(6), EX(6), EY(6)
133 DIM MC(399), BK(887), KS(73), KM(73), KF(73), KB(73), RV(24), RH(24)
140 FOR I = 1 TO 9: READ RX!(I), RY!(I): NEXT I
150 FOR I = 1 TO 3: READ SN$(I), SD$(I), SA(I): NEXT I
155 FOR I = 1 TO 6: READ EU(I), EV(I): NEXT I
157 FOR I = 1 TO 3: READ ZX(I), ZY(I), ZW(I), ZH(I): NEXT I
159 RESTORE 9615: FOR I = 1 TO 6: READ EX(I), EY(I): NEXT I: CMS(0) = 8: CMS(1) = 2: CMS(2) = &HFD30: CMK(0) = 8: CMK(1) = 2: CMK(2) = &HCF
160 BLOAD LD$ + "LMSHIP.SPR", VARPTR(SP(0))
170 BLOAD LD$ + "LMMASK.SPR", VARPTR(MK(0))
180 BLOAD LD$ + "FL1.SPR", VARPTR(F1(0)): BLOAD LD$ + "FL2.SPR", VARPTR(F2(0)): BLOAD LD$ + "FL3.SPR", VARPTR(F3(0))
182 BLOAD LD$ + "RC1.SPR", VARPTR(Q1(0)): BLOAD LD$ + "RC2.SPR", VARPTR(Q2(0)): BLOAD LD$ + "RC3.SPR", VARPTR(Q3(0))
184 BLOAD LD$ + "RC4.SPR", VARPTR(Q4(0)): BLOAD LD$ + "RC6.SPR", VARPTR(Q6(0))
186 BLOAD LD$ + "RC7.SPR", VARPTR(Q7(0)): BLOAD LD$ + "RC9.SPR", VARPTR(Q9(0))
187 BLOAD LD$ + "CP1.SPR", VARPTR(C1(0)): BLOAD LD$ + "CP2.SPR", VARPTR(C2(0)): BLOAD LD$ + "CP3.SPR", VARPTR(C3(0))
188 BLOAD LD$ + "CP4.SPR", VARPTR(C4(0)): BLOAD LD$ + "CP5.SPR", VARPTR(C5(0)): BLOAD LD$ + "CP6.SPR", VARPTR(C6(0))
189 BLOAD LD$ + "CP7.SPR", VARPTR(C7(0)): BLOAD LD$ + "CM1.SPR", VARPTR(M1(0)): BLOAD LD$ + "CM2.SPR", VARPTR(M2(0))
190 RP! = VARPTR(BK(0)): QB = RP! + 65536! * (RP! > 32767): RP! = VARPTR(KS(0)): QS = RP! + 65536! * (RP! > 32767): RP! = VARPTR(KM(0)): QM = RP! + 65536! * (RP! > 32767)
191 BLOAD LD$ + "CM3.SPR", VARPTR(M3(0)): BLOAD LD$ + "CM4.SPR", VARPTR(M4(0)): BLOAD LD$ + "CM5.SPR", VARPTR(M5(0))
192 BLOAD LD$ + "CM6.SPR", VARPTR(M6(0)): BLOAD LD$ + "CM7.SPR", VARPTR(M7(0))
193 BLOAD LD$ + "BRAKE.SPR", VARPTR(BK(0)): REM braking burn cutscene: 4 poses x ship, mask, flame (74 ints each)
194 BLOAD LD$ + "DU1.SPR", VARPTR(D1(0)): BLOAD LD$ + "DU2.SPR", VARPTR(D2(0)): BLOAD LD$ + "DU3.SPR", VARPTR(D3(0))
195 SCREEN 1, 0: COLOR 0, 1: PLAY "MB"
196 BLOAD LD$ + "DU4.SPR", VARPTR(D4(0)): BLOAD LD$ + "DU5.SPR", VARPTR(D5(0)): BLOAD LD$ + "DU6.SPR", VARPTR(D6(0))
197 BLOAD LD$ + "CKPIT.BIN", VARPTR(MC(0)): CA! = VARPTR(MC(0)): PR(0) = 0: CALL CA!(PR(0)): CS = PR(1): PR(0) = 1
198 IF CS THEN DEF SEG = CS: BLOAD LD$ + "CKCOM.DAT", 49408!: DEF SEG: REM 64K from DOS for the cockpit view scenery
199 PR(0) = 0: CALL CA!(PR(0)): SB = PR(1): RP! = VARPTR(H(0)): HP = RP! + 65536! * (RP! > 32767): REM 64K more: the site and its danger screens
200 REM ==== phase 1: orbit - drift left/right, then burn down to a site (no fuel, no points) ====
210 OUT &H3D8, &H6: CLS
220 DEF SEG = &HB800: BLOAD LD$ + "ORBIT.PIC", 0: DEF SEG
230 BX! = 146: BV! = 0: BY = 48: OX = -1: OZ = 0: OP = -1: PF = 0: FL = 0: MT! = 0: ZN = 2: T0! = TIMER
232 RESTORE 9600: READ NT: FOR I = 1 TO NT: READ TX(I), TY(I), TC(I): NEXT I: TS = 0: TW! = 0: BL! = 0
240 GOSUB 8950
245 IF INKEY$ <> "" THEN 245: REM ignore keys typed while the level was loading
250 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 250
255 IF DT! > .3 OR DT! < 0 THEN DT! = .3
260 T0! = T1!
265 K$ = INKEY$
266 IF K$ = "" AND JE% THEN JF% = 0: GOSUB 6800: K$ = JA$
267 IF K$ = "" THEN 300
270 IF K$ = CHR$(0) + "K" OR K$ = "4" OR K$ = "7" OR K$ = "1" THEN BV! = BV! - 10: PF = 4: PT! = T1! + .2
275 IF K$ = CHR$(0) + "M" OR K$ = "6" OR K$ = "9" OR K$ = "3" THEN BV! = BV! + 10: PF = 6: PT! = T1! + .2
280 IF K$ = CHR$(0) + "P" OR K$ = "2" OR K$ = CHR$(13) THEN 400
285 IF K$ = CHR$(27) THEN SK% = 1: PR(0) = 3: PR(1) = SB: CALL CA!(PR(0)): PR(1) = CS: CALL CA!(PR(0)): IF LD$ = "A:" THEN P$ = "INSERT THE START DISK": GOSUB 8900
286 IF K$ = CHR$(27) THEN GOSUB 8960: ON ERROR GOTO 8800: CHAIN "MOON"
290 GOTO 265
300 IF BV! > 60 THEN BV! = 60 ELSE IF BV! < -60 THEN BV! = -60
305 BV! = BV! * (1 - .6 * DT!): BX! = BX! + BV! * DT!
310 IF BX! < 4 THEN BX! = 4: BV! = 0 ELSE IF BX! > 288 THEN BX! = 288: BV! = 0
315 BI = INT(BX!): ZN = (BI + 14) \ 107 + 1: IF ZN > 3 THEN ZN = 3
320 IF T1! > PT! THEN PF = 0
325 IF ZN <> OZ THEN GOSUB 380
330 IF BI <> OX OR PF <> OP THEN XI = BI: YI = BY: GOSUB 5000
335 IF MT! > 0 THEN IF T1! > MT! THEN LINE (0, 16)-(319, 23), 0, BF: MT! = 0
337 GOSUB 2400
340 GOTO 250
380 REM ---- highlight the zone under the lander ----
382 IF OZ THEN LINE (ZX(OZ), ZY(OZ))-(ZW(OZ), ZH(OZ)), 0, B
384 LINE (ZX(ZN), ZY(ZN))-(ZW(ZN), ZH(ZN)), 2, B: OZ = ZN: SOUND 500, 1: RETURN
400 REM ---- descent: the up-facing thrusters push the lander down toward the site ----
405 IF SA(ZN) = 0 THEN M$ = SN$(ZN) + " - COMING SOON": LINE (0, 16)-(319, 23), 0, BF: LOCATE 3, 21 - LEN(M$) \ 2: PRINT M$;: SOUND 150, 4: MT! = T1! + 2.5: GOTO 265
410 LV = ZN: LS% = ZN: LN = 1: PLAY "T200O3L32CDEFGAB"
415 PF = 2: FOR J = 1 TO 10: XI = BI: YI = BY + 3 * J: GOSUB 5000
430 SOUND 120 - J * 8, 1: WD! = .1: GOSUB 7900: NEXT J
435 WD! = .4: GOSUB 7900
440 IF INKEY$ <> "" THEN 440
445 GOSUB 1200: GOTO 1000
1000 REM ==== load and start the level ====
1010 OUT &H3D8, &H6: CLS
1015 ON LV GOSUB 8700, 8710, 8720: READ PC$, MP$, X!, Y!, VX!, VY!, FM!, NP: FOR I = 1 TO NP: READ LA(I), LB(I), LM(I): NEXT I
1020 IF SB = 0 THEN DEF SEG = &HB800: BLOAD LD$ + PC$, 0: DEF SEG: BLOAD LD$ + MP$, VARPTR(H(0)): GOTO 1050
1025 IF LL <> LV THEN GOSUB 1100
1030 PR(0) = 4: PR(1) = SB: PR(2) = 1: PR(3) = HP: CALL CA!(PR(0)): REM show the site from memory, its map into H()
1050 SN = 1: MX = -1: F! = FM!: TH = 0: PF = 0: OX = -1: OF = -1: OP = -1
1060 GOSUB 8950
1070 LOCATE 1, 17: PRINT USING "LANDER #/3"; LN;
1080 LOCATE 4, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);
1090 T0! = TIMER: ST! = T0!: TT! = T0! + 3: HT! = 0
1092 TL = -1: LF! = 0: F7! = FM! * .15: CXM = 8 + INT(RND * 40): MV! = 0: CM = 0: SD = 0: CL = 0: F6 = 0: F3 = 0: A12! = 0: G12! = 0: IF RND < .15 THEN A12! = T0! + 4 + RND * 8
1093 NR = 0: RI = 0: REM the flight recorder: last 25 samples, 0.4 s apart
1094 GOSUB 2620
1096 GOTO 2000
1100 REM ---- the site and the danger screens either side, into memory once per site (slots 0 left, 1 site, 2 right) ----
1102 DEF SEG = SB: BLOAD LD$ + PC$, 16384: BLOAD LD$ + MP$, 50432!: C$ = LEFT$(PC$, LEN(PC$) - 4)
1104 BLOAD LD$ + C$ + "L.MAP", 49152!: BLOAD LD$ + C$ + "R.MAP", 51712!: BLOAD LD$ + C$ + "L.RLE", 53248!: DEF SEG
1106 PR(0) = 6: PR(1) = SB: PR(2) = 0: PR(3) = -12288: CALL CA!(PR(0))
1108 DEF SEG = SB: BLOAD LD$ + C$ + "R.RLE", 53248!: DEF SEG: PR(0) = 6: PR(2) = 2: CALL CA!(PR(0)): LL = LV: RETURN
1200 REM ==== braking burn: from orbit down toward the site, hands off (any key skips), no fuel used ====
1202 IF SB = 0 THEN RETURN
1204 OUT &H3D8, &H6: DEF SEG = SB: BLOAD LD$ + "BRAKE.RLE", 53248!: DEF SEG: PR(0) = 6: PR(1) = SB: PR(2) = -1: PR(3) = -12288: CALL CA!(PR(0))
1205 RP! = VARPTR(KF(0)): QF = RP! + 65536! * (RP! > 32767)
1206 GOSUB 8950: LOCATE 3, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);: M$ = "POWERED DESCENT": GOSUB 1250: OX = -1: J = -1: PN = 0: T0! = TIMER
1210 RP! = (TIMER - T0!) / 5: IF RP! > 1 OR INKEY$ <> "" THEN 1240
1212 XI = 12 + INT(210 * (1 - (1 - RP!) ^ 2)): YI = 40 + INT(36 * RP! * RP!): K = 0: IF RP! > .5 THEN K = INT((RP! - .5) * 8) + 1: IF K > 3 THEN K = 3
1214 IF K <> J THEN J = K: GOSUB 1230
1216 IF OX >= 0 THEN PUT (OX, OY), KB, PSET
1218 GET (XI, YI)-(XI + 23, YI + 23), KB: PUT (XI, YI), KM, AND: PUT (XI, YI), KS, OR: IF PN AND 1 THEN PUT (XI, YI), KF, OR
1220 OX = XI: OY = YI: PN = PN + 1: SOUND 40 + RND * 30, 1: GOTO 1210
1228 REM ---- pose K: copy its ship, mask and flame out of BK() into the arrays PUT uses (PUT can't take BK(n)) ----
1230 RP! = QB + 444! * K: PR(0) = 8: PR(4) = 74: PR(2) = RP! + 65536! * (RP! > 32767): PR(3) = QS: CALL CA!(PR(0))
1232 RP! = RP! + 148: PR(2) = RP! + 65536! * (RP! > 32767): PR(3) = QM: CALL CA!(PR(0)): RP! = RP! + 148: PR(2) = RP! + 65536! * (RP! > 32767): PR(3) = QF: CALL CA!(PR(0))
1234 IF K = 1 THEN M$ = "PITCHOVER": GOSUB 1250 ELSE IF K = 3 THEN M$ = "APPROACH PHASE": GOSUB 1250
1236 RETURN
1240 IF INKEY$ <> "" THEN 1240
1242 WD! = .5: GOSUB 7900: RETURN
1250 LINE (0, 8)-(319, 15), 0, BF: LOCATE 2, 21 - LEN(M$) \ 2: PRINT M$;: RETURN
2000 REM ==== main loop ====
2010 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 2010
2020 IF DT! > .3 OR DT! < 0 THEN DT! = .3
2030 T0! = T1!: LK = 0
2040 K$ = INKEY$
2042 IF K$ = "" AND JE% THEN JF% = 1: GOSUB 6800: K$ = JA$
2044 IF K$ = "" THEN 2100
2050 GOSUB 3000: IF Q THEN 200
2060 GOTO 2040
2100 A! = GR!
2110 IF TH > 0 THEN A! = GR! - AM! * TH / 10: F! = F! - BU! * TH / 10 * DT!: IF F! <= 0 THEN F! = 0: TH = 0
2120 VY! = VY! + A! * DT!: X! = X! + VX! * DT!: Y! = Y! + VY! * DT!
2130 IF X! < 4 THEN GOSUB 2810
2140 IF X! > 288 THEN GOSUB 2820
2150 IF Y! < -300 THEN Y! = -300: IF VY! < 0 THEN VY! = 0
2160 XI = INT(X!): YI = INT(Y!)
2170 IF YI + 22 >= H(320 + XI) THEN 4000
2180 FL = -(TH > 0) - (TH > 3) - (TH > 7)
2190 IF T1! > PT! THEN PF = 0
2195 IF DU THEN GOSUB 2300
2200 IF XI <> OX OR YI <> OY OR FL <> OF OR PF <> OP THEN IF YI < 46 THEN GOSUB 2660 ELSE GOSUB 5000
2205 Z = H(XI + 14) - YI - 22: IF Z < 30 THEN GOSUB 2340
2210 IF T1! >= HT! THEN GOSUB 6000: HT! = T1! + .4
2220 IF TT! > 0 THEN IF T1! > TT! THEN LINE (80, 24)-(239, 31), 0, BF: TT! = 0
2230 GOTO 2010
2300 REM ---- engine dust: erase last frame's plume (XOR again restores the ground exactly) ----
2305 ON DU GOSUB 2311, 2312, 2313, 2314, 2315, 2316: DU = 0: RETURN
2311 PUT (DX, DY), D1, XOR: RETURN
2312 PUT (DX, DY), D2, XOR: RETURN
2313 PUT (DX, DY), D3, XOR: RETURN
2314 PUT (DX, DY), D4, XOR: RETURN
2315 PUT (DX, DY), D5, XOR: RETURN
2316 PUT (DX, DY), D6, XOR: RETURN
2320 REM ---- engine dust: bigger plume the lower we are, two shimmer variants ----
2325 DU = 1 - 2 * (Z < 20) - 2 * (Z < 10) + (DC AND 1): DC = DC + 1
2330 DX = XI - 22: IF DX < 0 THEN DX = 0 ELSE IF DX > 248 THEN DX = 248
2335 DY = H(XI + 14) - 12: ON DU GOSUB 2311, 2312, 2313, 2314, 2315, 2316: RETURN
2340 REM ---- close to the ground (every frame): dust, contact light, tuck the shadow away ----
2342 IF TH > 2 THEN GOSUB 2320
2344 IF CL = 0 THEN IF Z < 5 AND VY! > 0 THEN CL = 1: M$ = "CONTACT LIGHT": MD! = 3: GOSUB 2500: SOUND 1500, 1
2346 IF Z < 16 THEN IF SD THEN GOSUB 2705
2348 RETURN
2400 REM ---- orbit life: the command module's light blinks, a star twinkles ----
2405 IF T1! > BL! THEN BL! = T1! + .5: BB = 1 - BB: PSET (160, 28), 2 * BB: PSET (161, 28), 2 * BB
2410 IF T1! < TW! THEN RETURN
2415 TW! = T1! + .2: IF TS THEN PSET (TX(TS), TY(TS)), TC(TS)
2420 TS = INT(RND * NT) + 1: IF RND < .5 THEN PSET (TX(TS), TY(TS)), 0 ELSE TS = 0
2425 RETURN
2500 REM ---- callout M$ on the message line for MD! seconds ----
2505 LINE (80, 24)-(239, 31), 0, BF: LOCATE 4, 21 - LEN(M$) \ 2: PRINT M$;: TT! = T1! + MD!: RETURN
2600 REM ---- the command module overhead (4x2 sprite): erase by putting back what was under it / draw ----
2605 IF CM = 0 THEN RETURN
2610 PUT (CXM, 36), CG, PSET: CM = 0: RETURN
2620 GET (CXM, 36)-(CXM + 3, 37), CG: PUT (CXM, 36), CMK, AND: PUT (CXM, 36), CMS, OR: CM = 1: RETURN
2650 REM ---- lander up near the module: take the module off, redraw the lander, put the module back ----
2652 GOSUB 2600: GOSUB 5000: GOSUB 2620: RETURN
2660 IF YI < 21 THEN 2670
2662 IF MX >= 0 THEN GOSUB 2680
2664 IF CM THEN 2652 ELSE 5000
2668 REM ---- above the top of the screen: the lander hides, a marker on the top edge shows where it is ----
2670 IF OX >= 0 THEN GOSUB 2600: PUT (OX - 4, OY - 3), BG, PSET: OX = -1: GOSUB 2620
2672 I = XI + 14: IF I < 2 THEN I = 2 ELSE IF I > 317 THEN I = 317
2674 IF I = MX THEN RETURN ELSE IF MX >= 0 THEN GOSUB 2680
2676 MX = I: LINE (MX - 2, 20)-(MX + 2, 20), 1: PSET (MX, 19), 1: RETURN
2680 LINE (MX - 2, 19)-(MX + 2, 20), 0, BF: MX = -1: RETURN
2700 REM ---- lander shadow on the surface (sun high on the right, shadow falls left): erase / draw ----
2705 PUT (SXO, SYO), SG, PSET: SD = 0: RETURN
2720 SXO = XI + 9 - INT(Z * .7): IF SXO < 0 THEN SXO = 0 ELSE IF SXO > 309 THEN SXO = 309
2725 H1 = H(SXO): H2 = H(SXO + 3): H3 = H(SXO + 6): H4 = H(SXO + 9): SYO = H1: SYB = H1
2726 IF H2 < SYO THEN SYO = H2 ELSE IF H2 > SYB THEN SYB = H2
2727 IF H3 < SYO THEN SYO = H3 ELSE IF H3 > SYB THEN SYB = H3
2728 IF H4 < SYO THEN SYO = H4 ELSE IF H4 > SYB THEN SYB = H4
2729 IF SYB - SYO > 30 OR SYB > 197 THEN RETURN
2730 GET (SXO, SYO)-(SXO + 9, SYB + 1), SG: LINE (SXO, H1)-(SXO + 3, H2), 0: LINE -(SXO + 6, H3), 0: LINE -(SXO + 9, H4), 0
2732 LINE (SXO, H1 + 1)-(SXO + 3, H2 + 1), 0: LINE -(SXO + 6, H3 + 1), 0: LINE -(SXO + 9, H4 + 1), 0: SD = 1: RETURN
2798 REM ---- off the side: flip to the danger screen there (or back), from memory ----
2800 IF DU THEN GOSUB 2300
2802 PR(0) = 4: PR(1) = SB: PR(2) = SN: PR(3) = HP: CALL CA!(PR(0)): OX = -1: SD = 0: CM = 0: MX = -1: TL = -1
2804 GOSUB 2620: LOCATE 1, 17: PRINT USING "LANDER #/3"; LN;: RETURN
2810 IF SN = 0 OR SB = 0 THEN X! = 4: VX! = 0: RETURN
2812 SN = SN - 1: X! = X! + 284: GOTO 2800
2820 IF SN = 2 OR SB = 0 THEN X! = 288: VX! = 0: RETURN
2822 SN = SN + 1: X! = X! - 284: GOTO 2800
3000 REM ---- one key ----
3005 IF K$ = "k" OR K$ = "K" THEN JE% = 0: STRIG OFF: RETURN
3010 Q = 0: K = 0
3020 IF LEN(K$) = 2 THEN K = INSTR("OPQKLMGHI", RIGHT$(K$, 1)): GOTO 3060
3030 IF K$ = CHR$(27) THEN Q = 1: RETURN
3040 IF K$ = "0" OR K$ = " " THEN TH = 0: RETURN
3050 IF K$ = "-" THEN K = 5 ELSE IF K$ = "+" THEN K = 8 ELSE K = INSTR("123456789", K$)
3060 IF K = 0 OR K = LK THEN RETURN
3065 LK = K
3070 IF K = 8 THEN TH = TH - (TH < 10 AND F! > 0): RETURN
3080 IF K = 5 THEN TH = TH + (TH > 0): RETURN
3090 IF F! < RF! THEN RETURN
3100 F! = F! - RF!: VX! = VX! + RX!(K) * DV!: VY! = VY! + RY!(K) * DV!
3110 PF = K: PT! = T1! + .2: RETURN
4000 REM ---- touchdown: which outcome? ----
4005 IF DU THEN GOSUB 2300
4006 IF SD THEN GOSUB 2700
4010 LF = H(XI + 1): RG = H(XI + 26): MN = H(320 + XI)
4020 P = 0: FOR I = 1 TO NP: IF XI + 1 > LA(I) AND XI + 26 < LB(I) THEN P = I
4030 NEXT I
4040 CT = 0: R$ = "": R2$ = "": D = SGN(VX!): IF D = 0 THEN D = 1
4050 IF ABS(VX!) > VXS! THEN CT = 3: IF ABS(VX!) > 3 AND F! > FM! * .25 AND RND < .2 THEN CT = 5
4060 IF CT = 0 AND (LF <> MN OR RG <> MN) THEN CT = 4
4062 IF CT = 0 AND SN <> 1 THEN CT = 4: REM the danger screens have nowhere safe
4070 IF CT = 0 AND VY! > VYS! THEN CT = 1
4080 IF VY! > 7 AND CT <> 5 THEN CT = 2
4085 IF TT! > 0 THEN LINE (80, 24)-(239, 31), 0, BF: TT! = 0
4090 YI = MN - 22: TH = 0: FL = 0: PF = 0: GOSUB 5000: GOSUB 6000
4100 CX = XI + 14: GC = H(CX): PO = 0
4110 IF CT THEN ON CT GOSUB 7100, 7200, 7300, 7400, 7500: GOTO 4400
4200 REM ==== landed: (soft landing + time bonus) x pad x lander ====
4205 IF P THEN W = LM(P) ELSE W = 1
4210 LT! = T1! - ST!: SF = 500 - INT(125 * VY! + 100 * ABS(VX!)): IF SF < 0 THEN SF = 0
4215 TB = 2000 - INT(50 * LT!): IF TB < 0 THEN TB = 0
4220 LP = 100: IF LN = 2 THEN LP = 50 ELSE IF LN = 3 THEN LP = 25
4225 TS! = INT(CSNG(SF + TB) * W * LP / 1000 + .5) * 10
4230 PLAY "T160O4L16CEG>C8": WD! = 1: GOSUB 7900: GOSUB 4800: IM = 0
4235 C$ = "TRANQUILITY BASE HERE.": R$ = "THE EAGLE HAS LANDED.": IF LV > 1 THEN R$ = "TOUCHDOWN CONFIRMED."
4237 IF LV = 2 THEN C$ = "FRA MAURO BASE HERE." ELSE IF LV = 3 THEN C$ = "HADLEY BASE HERE."
4240 LINE (62, 128)-(257, 189), 0, BF: LOCATE 17, 9 + (24 - LEN(C$)) \ 2: PRINT C$;: LOCATE 18, 9 + (24 - LEN(R$)) \ 2: PRINT R$;: WD! = .7: GOSUB 7900: WD! = .35
4245 LOCATE 19, 10: PRINT USING "SOFT LANDING    #####"; SF;: GOSUB 4295
4250 LOCATE 20, 10: PRINT USING "TIME BONUS      #####"; TB;: GOSUB 4295
4255 LOCATE 21, 10: PRINT USING "PAD X##   LANDER #/3"; W; LN;: GOSUB 4295
4260 LOCATE 22, 10: PRINT USING "SCORE          ######"; TS!;: PLAY "T200O5L16CEG>C8"
4270 LOCATE 23, 15: PRINT "PRESS ENTER";
4275 IF INKEY$ <> "" THEN 4275
4280 GOSUB 4700: K$ = INKEY$
4281 IF K$ = "" AND JE% THEN JF% = 0: GOSUB 6800: K$ = JA$
4282 IF K$ <> CHR$(13) THEN 4280
4285 GOTO 8000
4295 SOUND 700, 1: GOSUB 7900: RETURN
4400 REM ==== crashed: with landers left, a quick box and the next lander; the last one ends the level ====
4402 IF LN = 3 THEN 4470
4405 IM = 0: LINE (64, 60)-(255, 107), 0, BF: LINE (64, 60)-(255, 107), 2, B
4410 LOCATE 9, 21 - LEN(R$) \ 2: PRINT R$;
4415 LOCATE 10, 21 - LEN(R2$) \ 2: PRINT R2$;
4420 LOCATE 12, 14: PRINT USING "LANDERS LEFT #"; 3 - LN;: LOCATE 13, 10: PRINT "ENTER=NEXT  ESC=ORBIT";
4425 GOTO 4430
4430 IF INKEY$ <> "" THEN 4430
4440 GOSUB 4700: K$ = INKEY$
4441 IF K$ = "" AND JE% THEN JF% = 0: GOSUB 6800: K$ = JA$
4442 IF K$ = "" THEN 4440
4445 IF K$ = CHR$(27) THEN 200
4450 IF K$ <> CHR$(13) THEN 4440
4455 IF LN < 3 THEN LN = LN + 1: GOTO 1000
4460 GOTO 200
4470 REM ---- end of level, all three landers lost: the wreck, or the crater if the last one blew up ----
4472 WD! = .8: GOSUB 7900: PC$ = "WRECK.PIC": IF CT = 2 OR CT = 5 THEN PC$ = "CRATER.PIC"
4473 IM = 2 - (PC$ = "CRATER.PIC"): SP = 0: BB = 0: TW! = 0: FOR J = 1 TO 6: EB(J) = 1: NEXT J: FOR J = 1 TO 3: QY(J) = 999: NEXT J
4474 GOSUB 4600: LOCATE 1, 21 - LEN(R$) \ 2: PRINT R$;: LOCATE 2, 21 - LEN(R2$) \ 2: PRINT R2$;
4476 LOCATE 3, 21 - LEN(SN$(LV)) \ 2: PRINT SN$(LV);: LOCATE 4, 14: PRINT "MISSION FAILED";
4478 LOCATE 5, 15: PRINT "PRESS ENTER";: PLAY "T90O2L4GE-C2"
4479 GOTO 4430
4600 REM ---- end-of-level picture PC$ (LANDED, WRECK or CRATER), loaded with the display off ----
4610 OUT &H3D8, &H6: DEF SEG = &HB800: BLOAD LD$ + PC$, 0: DEF SEG: GOSUB 8950: RETURN
4700 REM ---- life on the end-of-level picture: IM 1 landed, 2 wreck, 3 crater ----
4702 IF IM = 0 THEN RETURN ELSE IF TIMER < TW! THEN RETURN
4704 TW! = TIMER + .15: TK = TK + 1: ON IM GOSUB 4710, 4720, 4740: RETURN
4710 IF TK MOD 4 = 0 THEN BB = 1 - BB: PSET (181, 62), 2 * BB: PSET (182, 62), 2 * BB
4712 RETURN
4720 IF TK MOD 3 = 0 THEN BB = 1 - BB: PSET (173, 56), 2 * BB: PSET (174, 56), 2 * BB
4722 IF SP THEN FOR J = 3 TO 1 STEP -1: PSET (QX(J), QY(J)), QC(J): NEXT J: SP = 0
4724 IF RND > .45 THEN RETURN
4726 FOR J = 1 TO 3: QX(J) = 200 + INT(RND * 14): QY(J) = 160 + INT(RND * 10): QC(J) = POINT(QX(J), QY(J)): PSET (QX(J), QY(J)), 2 + (J AND 1): NEXT J: SP = 1: RETURN
4740 J = INT(RND * 6) + 1: IF EB(J) THEN LINE (EX(J) - 1, EY(J))-(EX(J) + 1, EY(J)), 2 * -(RND < .7)
4742 IF TK MOD 25 = 0 THEN J = INT(RND * 6) + 1: IF EB(J) THEN EB(J) = 0: LINE (EX(J) - 1, EY(J))-(EX(J) + 1, EY(J)), 0
4744 FOR J = 1 TO 3: IF QY(J) < 200 THEN PSET (QX(J), QY(J)), QC(J)
4746 QY(J) = QY(J) + 1: IF QY(J) > 158 THEN QX(J) = 124 + INT(RND * 64): QY(J) = 128 + INT(RND * 10)
4748 QC(J) = POINT(QX(J), QY(J)): PSET (QX(J), QY(J)), 3: NEXT J: RETURN
4800 REM ==== success: the last seconds of the descent replayed out of the commander's window ====
4802 REM CKPIT.BIN draws the window: PR(2) altitude, PR(3) drift, PR(4) dust 0-3, PR(5) jolt
4805 OUT &H3D8, &H6: DEF SEG = &HB800: BLOAD LD$ + "COCKPIT.PIC", 0: DEF SEG: IF CS = 0 THEN GOSUB 8950: RETURN
4807 DEF SEG = CS: BLOAD LD$ + "CK" + CHR$(48 + LV) + ".DAT", 0: DEF SEG
4810 PR(1) = CS: PR(0) = 2: CALL CA!(PR(0)): PR(0) = 1: NS = NR: IF NS > 25 THEN NS = 25
4812 RO = (RI - NS + 26) MOD 25: XF = RD(RI): PN = 0: CL = 0: PR(5) = 0: I = 0: GOSUB 4840: PR(2) = Z: PR(3) = XD: CALL CA!(PR(0))
4814 LOCATE 17, 10: PRINT "DESCENT";: GOSUB 4870: GOSUB 4880: GOSUB 4885: GOSUB 8950
4816 IF INKEY$ <> "" THEN 4816 ELSE T0! = TIMER
4820 RP! = (TIMER - T0!) * 2.5: I = INT(RP!): IF I >= NS - 1 THEN 4860 ELSE IF I <> OI THEN GOSUB 4840
4825 RP! = RP! - I: PR(2) = Z + DA * RP!: PR(3) = XD + DD * RP!: CALL CA!(PR(0)): IF INKEY$ = "" THEN 4820 ELSE 4860
4838 REM ---- each new sample (0.4 s): where we are heading, dust, and one panel field (ALT every other time) ----
4840 OI = I: J = (RO + I) MOD 25: K = (J + 1) MOD 25: Z = RA(J): DA = RA(K) - Z: XD = RD(J) - XF: DD = RD(K) - RD(J)
4842 PR(4) = 0: IF RT(K) > 2 AND Z < 30 THEN PR(4) = 1 - (Z < 20) - (Z < 10)
4844 PN = PN + 1: ON PN MOD 6 + 1 GOSUB 4870, 4875, 4870, 4880, 4870, 4885: RETURN
4860 PR(2) = 0: PR(3) = 0: PR(4) = 3: PR(5) = 2: CALL CA!(PR(0)): SOUND 60, 2: LOCATE 17, 10: PRINT "TOUCHDOWN";: Z = 0: K = RI: GOSUB 4870: GOSUB 4875: GOSUB 4880
4862 PR(5) = 0: LOCATE 22, 10: PRINT "LIGHTS  CONTACT";: FOR I = 2 TO 0 STEP -1: PR(4) = I: WD! = .25: GOSUB 7900: CALL CA!(PR(0)): NEXT I
4864 LOCATE 22, 10: PRINT "ENGINE STOP    ";: GOSUB 4885: SOUND 200, 1: WD! = 1.2: GOSUB 7900: RETURN
4868 REM ---- the glass panel fields ----
4870 LOCATE 19, 10: PRINT USING "ALT  #### M"; Z * 5;: RETURN
4875 LOCATE 20, 10: PRINT USING "V/S  +##.# M/S"; -RV(K) / 10;: RETURN
4880 LOCATE 21, 10: PRINT USING "H/S  +##.# M/S"; RH(K) / 10;: RETURN
4885 AW = Z * 4 \ 3: IF AW > 53 THEN AW = 53
4886 LINE (22, 132)-(43, 185 - AW), 0, BF: IF AW > 0 THEN LINE (22, 186 - AW)-(43, 185), 1, BF
4887 IF CL = 0 AND Z < 5 THEN CL = 1: LOCATE 22, 10: PRINT "LIGHTS  CONTACT";: SOUND 1500, 1
4888 RETURN
5000 REM ---- draw lander: restore old background, save new, mask, ship, effects ----
5010 IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET
5020 GET (XI - 4, YI - 3)-(XI + 31, YI + 28), BG
5030 PUT (XI - 4, YI - 3), MK, AND: PUT (XI - 4, YI - 3), SP, OR
5040 ON FL GOSUB 5110, 5120, 5130
5050 ON PF GOSUB 5141, 5142, 5143, 5144, 5199, 5146, 5147, 5199, 5149
5060 OX = XI: OY = YI: OF = FL: OP = PF: RETURN
5110 PUT (XI - 4, YI - 3), F1, OR: RETURN
5120 PUT (XI - 4, YI - 3), F2, OR: RETURN
5130 PUT (XI - 4, YI - 3), F3, OR: RETURN
5141 PUT (XI - 4, YI - 3), Q1, OR: RETURN
5142 PUT (XI - 4, YI - 3), Q2, OR: RETURN
5143 PUT (XI - 4, YI - 3), Q3, OR: RETURN
5144 PUT (XI - 4, YI - 3), Q4, OR: RETURN
5146 PUT (XI - 4, YI - 3), Q6, OR: RETURN
5147 PUT (XI - 4, YI - 3), Q7, OR: RETURN
5149 PUT (XI - 4, YI - 3), Q9, OR: RETURN
5199 RETURN
6000 REM ---- HUD ----
6010 W = INT(F! / FM! * 78)
6020 IF W > 0 THEN LINE (42, 2)-(41 + W, 4), 1, BF
6030 IF W < 78 THEN LINE (42 + W, 2)-(119, 4), 0, BF
6040 AL = (H(XI + 14) - YI - 22) * 5: IF AL < 0 THEN AL = 0
6045 RI = (RI + 1) MOD 25: RA(RI) = AL \ 5: RD(RI) = INT((X! + 284 * (SN - 1)) * 4): RV(RI) = INT(VY! * 10): RH(RI) = INT(VX! * 10): RT(RI) = TH: NR = NR + 1
6050 LOCATE 2, 1: PRINT USING "ALT #### H+##.# V+##.# THR ###"; AL; VX!; -VY!; TH * 10;
6060 I = INT(T1! - ST!): IF I <> TL THEN TL = I: LOCATE 1, 32: PRINT USING "T ##"; I \ 60;: PRINT ":"; RIGHT$(STR$(100 + I MOD 60), 2);
6062 IF T1! > LF! THEN GOSUB 6100
6070 RETURN
6100 REM ---- once a second: callouts, the module drifts, the shadow follows ----
6105 LF! = T1! + 1: IF F! < F7! THEN GOSUB 6150
6110 IF A12! > 0 THEN IF T1! > A12! THEN A12! = 0: G12! = T1! + 2.8: M$ = "1202 PROGRAM ALARM": MD! = 2.6: GOSUB 2500: SOUND 880, 3: SOUND 660, 3: SOUND 880, 3
6115 IF G12! > 0 THEN IF T1! > G12! THEN G12! = 0: M$ = "GO ON THAT ALARM": MD! = 2: GOSUB 2500
6120 LT2 = 1 - LT2: IF LT2 THEN IF CXM < 308 THEN GOSUB 2600: CXM = CXM + 3: GOSUB 2620: RETURN ELSE RETURN
6125 Z = H(XI + 14) - YI - 22: IF CL THEN IF Z > 12 THEN CL = 0
6130 IF Z < 16 OR Z >= 90 THEN IF SD THEN GOSUB 2705: RETURN ELSE RETURN
6135 I = XI + 9 - INT(Z * .7): IF SD THEN IF ABS(I - SXO) < 3 THEN RETURN ELSE GOSUB 2705
6140 GOSUB 2720: RETURN
6150 IF F6 = 0 THEN F6 = 1: M$ = "60 SECONDS": MD! = 2.5: GOSUB 2500: SOUND 1000, 2: SOUND 32767, 1: SOUND 1000, 2: RETURN
6155 IF F3 = 0 AND F! < F7! / 2 THEN F3 = 1: M$ = "30 SECONDS": MD! = 2.5: GOSUB 2500: SOUND 1200, 2: SOUND 32767, 1: SOUND 1200, 2
6160 RETURN
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
7000 REM ---- draw crash pose PZ centred on column CX, resting on ground row GC ----
7010 IF PO THEN PUT (PX, PY), B2, PSET ELSE IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET: OX = -1
7020 PX = CX - 20: IF PX < 0 THEN PX = 0 ELSE IF PX > 280 THEN PX = 280
7030 PY = GC - 34: IF PY > 165 THEN PY = 165
7040 GET (PX, PY)-(PX + 39, PY + 33), B2: PO = 1
7050 ON PZ GOSUB 7061, 7062, 7063, 7064, 7065, 7066, 7067
7060 RETURN
7061 PUT (PX, PY), M1, AND: PUT (PX, PY), C1, OR: RETURN
7062 PUT (PX, PY), M2, AND: PUT (PX, PY), C2, OR: RETURN
7063 PUT (PX, PY), M3, AND: PUT (PX, PY), C3, OR: RETURN
7064 PUT (PX, PY), M4, AND: PUT (PX, PY), C4, OR: RETURN
7065 PUT (PX, PY), M5, AND: PUT (PX, PY), C5, OR: RETURN
7066 PUT (PX, PY), M6, AND: PUT (PX, PY), C6, OR: RETURN
7067 PUT (PX, PY), M7, AND: PUT (PX, PY), C7, OR: RETURN
7100 REM ---- 1 hard landing: legs fold, lander slumps ----
7110 DW = 18: GOSUB 7800: SOUND 70, 2
7120 PZ = 1: GOSUB 7000: DW = 24: GOSUB 7800: GOSUB 7850: WD! = .4: GOSUB 7900
7130 PZ = 2: GOSUB 7000: GOSUB 7850: SOUND 50, 3: WD! = .6: GOSUB 7900
7140 FOR J = 1 TO 6: PSET (CX + 6 + RND * 8, PY + 10 - RND * 10), 3: NEXT J
7150 R$ = "HARD LANDING": R2$ = "LANDING LEGS COLLAPSED": RETURN
7200 REM ---- 2 impact: fireball, debris, crater (PAINT is fast machine code) ----
7205 IF FR = 0 THEN FR = 18
7210 IF OX >= 0 THEN PUT (OX - 4, OY - 3), BG, PSET: OX = -1
7212 IF PO THEN PUT (PX, PY), B2, PSET: PO = 0
7214 FX = CX: FY = GC: GOSUB 7950: SOUND 40, 2
7220 FOR R = 6 TO FR STEP 6: CIRCLE (FX, FY - 8), R, 2: PAINT (FX, FY - 8), 2, 2
7225 CIRCLE (FX, FY - 8), R \ 3, 3: PAINT (FX, FY - 8), 3, 3: SOUND 37 + RND * 60, 1: NEXT R
7230 FOR Z = 1 TO 6: FOR J = 1 TO 6
7235 PSET (FX + EU(J) * Z, FY - 8 - EV(J) * Z + Z * Z), 3 - (J AND 1)
7240 NEXT J: NEXT Z
7245 WD! = .25: GOSUB 7900
7250 PUT (GX, GY), FB, PSET: CIRCLE (FX, FY - 8), FR, 2: CIRCLE (FX, FY - 8), FR - 3, 2: WD! = .2: GOSUB 7900
7255 PUT (GX, GY), FB, PSET: CIRCLE (FX, FY - 8), FR + 4, 2: WD! = .15: GOSUB 7900
7260 PUT (GX, GY), FB, PSET
7275 FOR J = -16 TO 16: I = FX + J: IF I >= 0 AND I < 320 THEN Z = INT(4 * (1 - (J / 16) ^ 2)): LINE (I, H(I) - 1)-(I, H(I) + Z), 0
7280 NEXT J
7285 FOR J = 0 TO 7: I = FX + INT(RND * 40) - 20: IF I >= 0 AND I < 319 THEN PSET (I, H(I) - 2), 2 + (J MOD 2)
7290 NEXT J
7295 IF R$ = "" THEN R$ = "IMPACT": R2$ = "LANDER DESTROYED"
7298 FR = 0: RETURN
7300 REM ---- 3 sideways: a foot catches, tips over and rolls ----
7310 SOUND 90, 1: PZ = 4 + (D > 0): CX = CX + 3 * D: GOSUB 7000: DW = 16: GOSUB 7800: WD! = .3: GOSUB 7900
7320 PZ = 6 + (D > 0): CX = CX + 6 * D: GC = H(CX): GOSUB 7000: GOSUB 7800: GOSUB 7850: SOUND 60, 3: WD! = .5: GOSUB 7900
7330 FOR J = 1 TO 3: PSET (PX + 20 - 12 * D, PY + 14), 1: WD! = .3: GOSUB 7900: PSET (PX + 20 - 12 * D, PY + 14), 0: GOSUB 7900: NEXT J
7340 R$ = "TIPPED OVER": R2$ = "DRIFTING SIDEWAYS": RETURN
7400 REM ---- 4 steep ground: slides downhill and flips ----
7405 D = SGN(RG - LF): IF D = 0 THEN D = 1
7410 PZ = 4 + (D > 0): CX = CX + 4 * D: GC = H(CX): GOSUB 7000: DW = 12: GOSUB 7800: WD! = .35: GOSUB 7900
7420 CX = CX + 6 * D: GC = H(CX): GOSUB 7000: GOSUB 7800: WD! = .3: GOSUB 7900
7430 PZ = 7: CX = CX + 6 * D: GC = H(CX): GOSUB 7000: DW = 18: GOSUB 7800: SOUND 55, 3: WD! = .6: GOSUB 7900
7440 R$ = "SLID OFF THE RIM": R2$ = "GROUND TOO STEEP": IF SN <> 1 THEN R$ = "NO SAFE GROUND": R2$ = "ROCKS AND STEEP SLOPES"
7442 RETURN
7500 REM ---- 5 rare: impact jams the main engine on and a side thruster firing ----
7510 R$ = "MAYDAY": R2$ = "THRUSTER MALFUNCTION": GOSUB 7850: SOUND 100, 1
7520 VY! = -2: VX! = VX! + 2 * D: Y! = YI - 1: X! = XI: T0! = TIMER: AT! = 0: ALM = 0: RL! = F! / 1.5: IF RL! < 100 THEN RL! = 100
7540 T1! = TIMER: DT! = T1! - T0!: IF DT! < .05 AND DT! >= 0 THEN 7540
7550 IF DT! > .5 OR DT! < 0 THEN DT! = .5
7560 T0! = T1!: K$ = INKEY$
7570 A! = GR!: IF F! > 0 THEN A! = GR! - AM! * .6: F! = F! - RL! * DT!: IF F! < 0 THEN F! = 0
7580 VX! = VX! + 3 * D * DT!: VY! = VY! + A! * DT!: X! = X! + VX! * DT!: Y! = Y! + VY! * DT!
7590 IF X! < 4 THEN X! = 4: VX! = 0
7600 IF X! > 288 THEN X! = 288: VX! = 0
7610 IF Y! < 21 THEN Y! = 21: IF VY! < 0 THEN VY! = 0
7620 XI = INT(X!): YI = INT(Y!)
7630 IF YI + 22 >= H(320 + XI) THEN 7690
7640 FL = 3 * -(F! > 0): PF = 6 + 2 * (D < 0)
7650 GOSUB 5000: PSET (XI + 14 - 23 * D, YI + 14), 3: PSET (XI + 15 - 23 * D, YI + 13), 3
7660 IF T1! > AT! THEN AT! = T1! + .3: ALM = 1 - ALM: GOSUB 7700
7670 IF T1! >= HT! THEN GOSUB 6000: HT! = T1! + .25
7680 GOTO 7540
7690 YI = H(320 + XI) - 22: FL = 0: PF = 0: GOSUB 5000: LINE (110, 22)-(209, 33), 0, BF
7695 CX = XI + 14: GC = H(CX): FR = 24: GOSUB 7200: RETURN
7700 IF ALM THEN LINE (110, 22)-(209, 33), 2, B: LOCATE 4, 15: PRINT "MASTER ALARM";: SOUND 880, 1 ELSE LINE (110, 22)-(209, 33), 0, BF: SOUND 660, 1
7710 RETURN
7800 REM ---- dust kicked up around CX, half-width DW ----
7810 FOR J = 1 TO 14: Z = CX + INT(RND * 2 * DW) - DW
7820 IF Z >= 0 AND Z < 320 THEN PSET (Z, H(Z) - 1 - INT(RND * 3)), 3
7830 NEXT J: RETURN
7850 REM ---- sparks ----
7860 FOR J = 1 TO 8: PSET (CX + RND * 24 - 12, GC - 2 - RND * 14), 2: NEXT J: RETURN
7900 REM ---- wait WD! seconds ----
7910 T2! = TIMER + WD!
7920 IF TIMER < T2! THEN 7920
7930 RETURN
7950 REM ---- save the 64x56 area around the crash before the fireball ----
7960 GX = FX - 32: IF GX < 0 THEN GX = 0 ELSE IF GX > 256 THEN GX = 256
7970 GY = FY - 38: IF GY < 18 THEN GY = 18 ELSE IF GY > 144 THEN GY = 144
7980 GET (GX, GY)-(GX + 63, GY + 55), FB: RETURN
8000 REM ==== mission complete: high score check, initials, save, show table ====
8005 IF LD$ = "A:" THEN P$ = "INSERT THE START DISK": GOSUB 8900: REM one drive: the scores live on the START disk
8010 GOSUB 8100: HR = 0
8020 IF TS! > HS!(10) THEN GOSUB 8400
8030 GOSUB 8500: LOCATE 20, 14: PRINT "PRESS ANY KEY";
8035 IF HR > 0 AND HE THEN LOCATE 21, 12: PRINT "(DISK ERROR: NOT SAVED)";
8040 IF INKEY$ = "" THEN 8040
8045 IF LD$ = "A:" THEN P$ = "INSERT THE LUNAR LANDING DISK": GOSUB 8900
8050 GOTO 200
8100 REM ---- load the high score table (empty until the first scores are saved in LANDHS.DAT) ----
8110 HE = 0: ON ERROR GOTO 8180
8120 OPEN "LANDHS.DAT" FOR INPUT AS #1
8130 IF HE = 0 THEN FOR I = 1 TO 10: INPUT #1, HN$(I), HS!(I), HL$(I): NEXT I
8140 CLOSE #1: ON ERROR GOTO 0
8150 IF HE THEN FOR I = 1 TO 10: HN$(I) = "": HS!(I) = 0: HL$(I) = "": NEXT I
8160 RETURN
8180 HE = 1: RESUME NEXT
8300 REM ---- save the table ----
8310 HE = 0: ON ERROR GOTO 8180
8320 OPEN "LANDHS.DAT" FOR OUTPUT AS #1
8330 IF HE = 0 THEN FOR I = 1 TO 10: WRITE #1, HN$(I), HS!(I), HL$(I): NEXT I
8340 CLOSE #1: ON ERROR GOTO 0: RETURN
8400 REM ---- new high score: find the rank, type initials, insert, save ----
8410 HR = 10
8415 IF HR > 1 THEN IF TS! > HS!(HR - 1) THEN HR = HR - 1: GOTO 8415
8420 LINE (56, 52)-(263, 139), 0, BF: LINE (64, 60)-(255, 123), 1, B
8425 PLAY "T180O4L16CDEFGAB>C8"
8430 LOCATE 9, 13: PRINT "NEW HIGH SCORE!";
8435 LOCATE 10, 13: PRINT USING "RANK ##  ######"; HR; TS!;
8440 LOCATE 12, 12: PRINT "TYPE YOUR INITIALS";
8445 N$ = ""
8450 LOCATE 14, 19: PRINT LEFT$(N$ + "___", 3);
8455 K$ = INKEY$: IF K$ = "" THEN 8455
8460 IF K$ >= "a" AND K$ <= "z" THEN K$ = CHR$(ASC(K$) - 32)
8465 IF LEN(K$) = 1 AND LEN(N$) < 3 AND ((K$ >= "A" AND K$ <= "Z") OR (K$ >= "0" AND K$ <= "9")) THEN N$ = N$ + K$: SOUND 800, 1
8470 IF K$ = CHR$(8) AND LEN(N$) > 0 THEN N$ = LEFT$(N$, LEN(N$) - 1)
8475 IF K$ <> CHR$(13) OR N$ = "" THEN 8450
8480 IF HR < 10 THEN FOR I = 10 TO HR + 1 STEP -1: HN$(I) = HN$(I - 1): HS!(I) = HS!(I - 1): HL$(I) = HL$(I - 1): NEXT I
8485 HN$(HR) = N$: HS!(HR) = TS!: HL$(HR) = LEFT$(SN$(LV), 12)
8490 GOSUB 8300: RETURN
8500 REM ---- draw the high score table; HR = rank to highlight (0 = none) ----
8510 LINE (32, 44)-(287, 171), 0, BF: LINE (32, 44)-(287, 171), 1, B
8520 LOCATE 7, 15: PRINT "HIGH SCORES";: LINE (116, 57)-(203, 57), 1
8530 FOR I = 1 TO 10: LOCATE 8 + I, 7: IF HS!(I) > 0 THEN PRINT USING "##. \ \  ######  "; I; HN$(I); HS!(I);: PRINT HL$(I); ELSE PRINT USING "##.  ---"; I;
8535 NEXT I
8540 IF HR THEN LINE (44, 55 + 8 * HR)-(277, 64 + 8 * HR), 2, B
8550 RETURN
8690 REM ---- point READ at the chosen site's level data ----
8700 RESTORE 9110: RETURN
8710 RESTORE 9130: RETURN
8720 RESTORE 9150: RETURN
8800 IF LD$ = "A:" THEN RESUME 8805 ELSE RESUME 8810: REM MOON not found: one drive asks for the START disk, else back to DOS
8805 P$ = "START DISK NOT FOUND": GOSUB 8900: ON ERROR GOTO 8800: CHAIN "MOON"
8810 SCREEN 0, 0: WIDTH 80: SYSTEM
8890 REM ---- one drive: ask for disk P$ in drive A: ----
8900 LINE (16, 60)-(303, 107), 0, BF: LINE (16, 60)-(303, 107), 2, B: LOCATE 10, 21 - LEN(P$) \ 2: PRINT P$;: LOCATE 12, 7: PRINT "IN DRIVE A: AND PRESS A KEY";
8905 SOUND 200, 3: IF INKEY$ <> "" THEN 8905
8910 K$ = INKEY$
8911 IF K$ = "" AND JE% THEN JF% = 0: GOSUB 6800: K$ = JA$
8912 IF K$ = "" THEN 8910
8915 RETURN
8940 REM ---- display on, palette cyan / red / grey (CGA: the mode register's B/W bit). A Tandy 1000 picks palette registers 3, 4, 7 for that, so open its palette mask (it masks them to 0-3) and set them ----
8950 OUT &H3D8, &HE: OUT &H3D9, 0: IF TY = 0 THEN RETURN
8952 I = INP(&H3DA): OUT &H3DA, 1: OUT &H3DE, &HF: OUT &H3DA, &H10: OUT &H3DE, 0: OUT &H3DA, &H13: OUT &H3DE, 3: OUT &H3DA, &H14: OUT &H3DE, 4: OUT &H3DA, &H17: OUT &H3DE, 7: RETURN
8958 REM ---- before CHAIN: erase the arrays, newest first. CHAIN otherwise drops every non-COMMON variable one at a time, shifting all the arrays each time (minutes on an XT) ----
8960 ERASE RH, RV, KB, KF, KM, KS, BK, MC, EY, EX, EB, QC, QY, QX, TC, TY
8961 ERASE TX, SG, CG, CMK, CMS, D6, D5, D4, D3, D2, D1, ZH, ZW, ZY, ZX, HL$
8962 ERASE HS!, HN$, SA, SD$, SN$, RY!, RX!, LM, LB, LA, EV, EU, M7, M6, M5, M4
8963 ERASE M3, M2, M1, C7, C6, C5, C4, C3, C2, C1, FB, B2, Q9, Q7, Q6, Q4
8964 ERASE Q3, Q2, Q1, F3, F2, F1, BG, MK, SP, H, RT, RD, RA, PR
8965 RETURN
9000 REM ---- thrusters: push x, push y for keys 1-9 (5 and 8 are throttle) ----
9010 DATA -.707,.707, 0,1, .707,.707, -1,0, 0,0, 1,0, -.707,-.707, 0,0, .707,-.707
9055 REM ---- landing sites: name, description, available? ----
9060 DATA "TRANQUILITY BASE", "APOLLO 11 - EASY", 1
9070 DATA "FRA MAURO", "APOLLO 14 - MEDIUM", 1
9080 DATA "HADLEY RILLE", "APOLLO 15 - HARD", 1
9090 REM ---- debris directions for the explosion (x step, upward step) ----
9095 DATA -5,6, -3,8, -1,9, 2,9, 4,7, 5,5
9096 REM ---- phase 1 zone highlight boxes (x0, y0, x1, y1), matching ORBIT.PIC ----
9097 DATA 5,117,97,137, 117,109,193,129, 213,117,313,137
9100 REM ---- levels: picture, map, start x, y, x speed, y speed, fuel, pads (left x, right x, multiplier) ----
9110 DATA "EASY.PIC", "EASY.MAP", 40, 24, 6, 1, 800, 3, 12,68,2, 140,184,3, 256,292,5
9120 REM Fra Mauro: rolling hills, a ridge to climb, boulders, Cone crater
9130 DATA "MEDIUM.PIC", "MEDIUM.MAP", 40, 24, 8, 1, 700, 3, 18,64,3, 150,190,5, 270,304,7
9140 REM Hadley Rille: Mount Hadley, the x7 pad down in the rille, the x10 mesa by Hadley Delta
9150 DATA "HARD.PIC", "HARD.MAP", 20, 24, 10, 1, 650, 3, 8,48,4, 190,224,7, 282,313,10
9596 REM ---- orbit stars that twinkle: count, then x, y, colour (tools/mkstars.py on ORBIT.PIC) ----
9600 DATA 14,13,35,3,33,33,3,39,123,3,43,118,1,65,29,1,67,28,1,67,33,3,73,39
9601 DATA 3,92,39,3,97,34,3,298,130,3,307,32,1,312,133,1,313,129,3
9605 REM ---- crater embers x, y (the module overhead is built in line 159: 4x2 sprite and mask) ----
9615 DATA 100,164, 206,162, 190,186, 240,166, 170,190, 96,182
