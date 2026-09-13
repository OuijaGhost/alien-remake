# Every address the remake cites

**Generated — do not hand-edit.** Run `python tools/gen_memory_map.py`.

The citations themselves live in the source, where someone about to change a
line will see them. This is the same set sorted by address, so you can ask *what
relies on `$7569`?* without grepping — and so the provenance survives even if a
comment is lost.

Names come from `alien.sym` and the labels in `ALIEN.annotated.asm`; an
address with no name is usually a data cell rather than a routine entry.

| | |
|---|---|
| distinct addresses cited | **1141** |
| of those, named in the disassembly | **169** |
| modules carrying citations | **42** |

## By address

| address | name | referenced from |
|---|---|---|
| `$0020` | — | `audio/sfx.py`:124, 131, 137 |
| `$0100` | — | `audio/sfx.py`:93<br>`core/sim/__init__.py`:937 |
| `$0314` | — | `audio/intro.py`:5 |
| `$0315` | — | `audio/intro.py`:5 |
| `$0340` | — | `render/frontend.py`:102, 936 |
| `$03FF` | — | `render/endscreen.py`:89, 100 |
| `$0400` | — | `core/gamedata_snapshot.py`:61<br>`render/deck_backdrop.py`:6, 71<br>`render/frontend.py`:158, 751, 1210, 1228<br>`render/play.py`:491, 532, 1126<br>`render/pygame_app.py`:133, 203<br>`render/text.py`:14, 126<br>`screens/ending.py`:10, 32, 64 |
| `$0431` | — | `core/constants.py`:740<br>`render/frontend.py`:204 |
| `$0436` | — | `core/constants.py`:740<br>`render/frontend.py`:204 |
| `$043B` | — | `core/constants.py`:740<br>`render/frontend.py`:204 |
| `$0440` | — | `core/constants.py`:740<br>`render/frontend.py`:204 |
| `$0445` | — | `core/constants.py`:740<br>`render/frontend.py`:204 |
| `$0452` | — | `render/frontend.py`:166 |
| `$0456` | — | `render/frontend.py`:159 |
| `$046E` | — | `core/menu.py`:313<br>`core/orders.py`:45, 47<br>`core/sim/orders.py`:602 |
| `$0478` | — | `render/endscreen.py`:186, 234<br>`screens/ending.py`:44, 50, 57, 64, 69 |
| `$0480` | — | `render/endscreen.py`:235<br>`screens/ending.py`:50, 56, 67 |
| `$04A6` | — | `render/frontend.py`:167 |
| `$04F0` | — | `render/endscreen.py`:198<br>`screens/ending.py`:26, 64 |
| `$0509` | — | `render/frontend.py`:168 |
| `$0540` | — | `render/endscreen.py`:200<br>`screens/ending.py`:27, 65 |
| `$0546` | — | `render/frontend.py`:169 |
| `$0590` | — | `render/endscreen.py`:201<br>`screens/ending.py`:28, 38, 65 |
| `$05D6` | — | `render/play.py`:688<br>`screens/panels.py`:117, 118 |
| `$05EB` | — | `render/endscreen.py`:57, 85 |
| `$05FE` | — | `render/play.py`:690<br>`screens/panels.py`:117, 119 |
| `$0608` | — | `render/frontend.py`:170<br>`screens/ending.py`:30, 65, 80 |
| `$061D` | — | `render/frontend.py`:1012<br>`render/layout.py`:23 |
| `$0630` | — | `screens/ending.py`:81 |
| `$064E` | — | `core/menu.py`:564, 568, 571, 583, 586, 589…<br>`core/orders.py`:46<br>`core/sim/__init__.py`:531<br>`render/play.py`:652<br>`screens/panels.py`:66, 129 |
| `$0676` | — | `core/menu.py`:488, 489<br>`core/orders.py`:57<br>`core/sim/orders.py`:318<br>`render/play.py`:652<br>`screens/panels.py`:67, 129 |
| `$06D0` | — | `screens/panels.py`:161 |
| `$06E8` | — | `render/frontend.py`:1210, 1228 |
| `$06F9` | — | `core/opening_name.py`:10<br>`render/frontend.py`:49, 51, 1242 |
| `$0701` | — | `core/opening_name.py`:11<br>`render/frontend.py`:50, 51, 1243, 1256 |
| `$0702` | — | `render/play.py`:366 |
| `$070E` | — | `render/play.py`:368 |
| `$0711` | — | `render/play.py`:849, 856 |
| `$0752` | — | `render/play.py`:367 |
| `$0767` | — | `core/crew.py`:221 |
| `$0770` | — | `render/play.py`:312, 369<br>`screens/ending.py`:73 |
| `$0773` | — | `render/frontend.py`:205 |
| `$077B` | — | `render/play.py`:313 |
| `$0783` | — | `screens/ending.py`:73 |
| `$0784` | — | `screens/ending.py`:73 |
| `$0786` | — | `render/play.py`:313 |
| `$078E` | — | `render/play.py`:313 |
| `$0798` | — | `render/play.py`:913<br>`screens/panels.py`:214, 218 |
| `$07A8` | — | `screens/panels.py`:215 |
| `$07C0` | — | `core/constants.py`:582<br>`core/sim/specials.py`:175<br>`core/state.py`:169, 170<br>`render/play.py`:910, 1042<br>`screens/panels.py`:191, 203 |
| `$07CA` | — | `screens/panels.py`:203 |
| `$07D7` | — | `render/frontend.py`:205 |
| `$07D8` | — | `render/endscreen.py`:277<br>`render/frontend.py`:180<br>`screens/ending.py`:74, 78 |
| `$07E7` | — | `render/deck_backdrop.py`:6 |
| `$07F8` | — | `render/frontend.py`:101, 935<br>`render/layout.py`:43<br>`render/play.py`:100<br>`render/pygame_app.py`:182, 310 |
| `$07F9` | — | `render/play.py`:123, 1195 |
| `$07FA` | — | `render/frontend.py`:121<br>`render/play.py`:963 |
| `$07FB` | — | `render/play.py`:172 |
| `$07FE` | — | `render/layout.py`:43<br>`render/play.py`:162 |
| `$07FF` | — | `render/play.py`:162 |
| `$0800` | — | `audio/sfx.py`:183 |
| `$2000` | — | `audio/intro.py`:31<br>`render/deck_backdrop.py`:12<br>`render/pygame_app.py`:253, 707<br>`render/romfont.py`:7<br>`render/tiles.py`:32, 52 |
| `$3200` | — | `audio/sfx.py`:156 |
| `$3240` | — | `render/frontend.py`:127<br>`render/tiles.py`:35 |
| `$343F` | — | `render/frontend.py`:127<br>`render/tiles.py`:35 |
| `$3FFF` | — | `render/deck_backdrop.py`:12<br>`render/tiles.py`:32, 52 |
| `$400A` | `set_charbase` | `render/frontend.py`:949, 1071<br>`render/pygame_app.py`:707<br>`render/romfont.py`:7 |
| `$402B` | — | `core/constants.py`:1043 |
| `$4032` | — | `core/constants.py`:1028, 1042<br>`core/sim/__init__.py`:390<br>`core/sim/specials.py`:502 |
| `$403A` | — | `core/constants.py`:1017, 1019, 1037<br>`core/sim/__init__.py`:390<br>`core/sim/orders.py`:224, 647<br>`core/sim/specials.py`:502 |
| `$4042` | `compute_action_delay` | `core/constants.py`:987, 988, 1047<br>`core/sim/orders.py`:524, 546 |
| `$405D` | — | `core/constants.py`:990, 1004 |
| `$4064` | — | `core/constants.py`:990, 1004 |
| `$40B8` | — | `core/constants.py`:967<br>`core/gamedata_snapshot.py`:41<br>`core/map.py`:179 |
| `$40FA` | — | `core/constants.py`:967<br>`core/gamedata_snapshot.py`:41<br>`core/map.py`:179 |
| `$413C` | — | `core/alien.py`:25, 32, 681, 685, 692, 721…<br>`core/constants.py`:408, 438, 439, 457 |
| `$4152` | — | `core/alien.py`:25, 692, 716, 722, 756, 772… |
| `$4155` | — | `core/alien.py`:757<br>`core/constants.py`:466 |
| `$4157` | — | `core/alien.py`:786 |
| `$4185` | — | `core/constants.py`:442 |
| `$4189` | — | `core/alien.py`:778 |
| `$418E` | — | `core/alien.py`:779 |
| `$41AA` | — | `core/alien.py`:788 |
| `$41B8` | — | `core/alien.py`:717, 790 |
| `$41C4` | — | `core/alien.py`:717, 792 |
| `$41C7` | — | `core/constants.py`:470 |
| `$41CB` | — | `core/constants.py`:470 |
| `$41F7` | — | `core/alien.py`:25, 756, 796 |
| `$4230` | — | `core/alien.py`:748, 797<br>`core/constants.py`:376, 385<br>`render/audio.py`:207 |
| `$4292` | `alien_death_effects` | `core/alien.py`:805<br>`core/state.py`:104 |
| `$429E` | — | `core/alien.py`:807 |
| `$42A1` | — | `core/state.py`:107 |
| `$4303` | `var_game_mode` | `core/flow.py`:64, 344 |
| `$4304` | `game_init_mode` | `core/flow.py`:345 |
| `$4317` | — | `core/flow.py`:63<br>`render/frontend.py`:944 |
| `$4327` | — | `core/flow.py`:67<br>`render/frontend.py`:964 |
| `$4371` | — | `render/frontend.py`:149, 974 |
| `$437E` | — | `render/frontend.py`:149, 974 |
| `$4389` | — | `core/constants.py`:783<br>`render/frontend.py`:173 |
| `$4390` | — | `audio/sfx.py`:145, 328 |
| `$439F` | — | `audio/sfx.py`:148<br>`render/frontend.py`:1016 |
| `$43B8` | — | `audio/sfx.py`:149<br>`render/frontend.py`:1016 |
| `$43CB` | — | `render/frontend.py`:1016 |
| `$43CD` | — | `audio/sfx.py`:150<br>`core/sound.py`:30 |
| `$43D0` | — | `core/constants.py`:783<br>`core/flow.py`:111<br>`render/frontend.py`:173 |
| `$43D3` | — | `render/frontend.py`:964 |
| `$43E5` | `prompt_and_wait` | `core/flow.py`:290 |
| `$4405` | — | `core/flow.py`:62, 277, 347<br>`render/frontend.py`:942 |
| `$441F` | — | `core/flow.py`:279, 281<br>`render/frontend.py`:945 |
| `$4425` | — | `core/flow.py`:280<br>`render/frontend.py`:946 |
| `$4429` | — | `core/flow.py`:281 |
| `$443C` | — | `render/frontend.py`:156, 158 |
| `$4457` | — | `render/frontend.py`:156, 159 |
| `$4460` | — | `render/frontend.py`:139<br>`render/pygame_app.py`:1283 |
| `$4463` | — | `render/frontend.py`:161, 166 |
| `$4471` | — | `render/frontend.py`:144, 167 |
| `$4492` | — | `render/frontend.py`:145, 168 |
| `$44A0` | — | `render/frontend.py`:146, 169 |
| `$44B3` | — | `render/frontend.py`:139 |
| `$44BC` | — | `core/constants.py`:677<br>`render/play.py`:108 |
| `$44C1` | — | `audio/sfx.py`:334<br>`render/frontend.py`:170 |
| `$44D6` | — | `audio/sfx.py`:178<br>`render/frontend.py`:172<br>`render/layout.py`:23 |
| `$44FF` | — | `render/frontend.py`:161 |
| `$4500` | — | `audio/sfx.py`:148<br>`render/frontend.py`:176<br>`render/layout.py`:24 |
| `$451C` | — | `core/constants.py`:644<br>`core/state.py`:141<br>`render/play.py`:1052 |
| `$452A` | — | `audio/sfx.py`:150<br>`render/frontend.py`:178<br>`render/layout.py`:24 |
| `$453C` | — | `core/constants.py`:644<br>`core/state.py`:141<br>`render/pygame_app.py`:1290 |
| `$4554` | — | `audio/sfx.py`:149<br>`render/frontend.py`:177<br>`render/layout.py`:24 |
| `$457F` | `var_damage_room_idx` | `core/sim/__init__.py`:337, 340 |
| `$4581` | `find_colocated_crew` | `core/menu.py`:358 |
| `$45AA` | — | `core/menu.py`:362 |
| `$45B1` | — | `core/menu.py`:362 |
| `$45B9` | — | `core/sim/orders.py`:247, 264 |
| `$45D3` | — | `core/constants.py`:122<br>`core/sim/orders.py`:533, 538 |
| `$45E7` | `scripted_event_check` | `core/sim/orders.py`:529 |
| `$45FD` | — | `core/sim/orders.py`:538 |
| `$4622` | — | `core/sim/orders.py`:535 |
| `$4625` | — | `core/constants.py`:377 |
| `$4639` | — | `core/sim/orders.py`:535 |
| `$463C` | — | `core/constants.py`:377 |
| `$4662` | — | `core/sim/orders.py`:534 |
| `$4665` | — | `core/constants.py`:379<br>`core/sim/orders.py`:533 |
| `$466B` | — | `core/sim/orders.py`:534 |
| `$466E` | — | `core/constants.py`:379 |
| `$4690` | — | `core/sim/orders.py`:532 |
| `$4781` | `var_alien_aggression` | `core/alien.py`:284, 607, 608<br>`core/constants.py`:227, 228, 232, 899<br>`core/sim/__init__.py`:336, 344, 345, 346, 347 |
| `$4784` | `init_char_turn` | `core/constants.py`:896<br>`core/sim/__init__.py`:328, 333 |
| `$47A8` | — | `core/sim/__init__.py`:362 |
| `$47DC` | — | `core/constants.py`:376, 386<br>`core/sim/__init__.py`:167, 781<br>`core/sim/protocol.py`:44 |
| `$47F1` | — | `core/constants.py`:899 |
| `$47F4` | — | `core/constants.py`:903 |
| `$47F8` | — | `core/constants.py`:899<br>`core/sim/__init__.py`:376 |
| `$47FE` | — | `core/sim/__init__.py`:343 |
| `$4806` | — | `core/constants.py`:901, 902 |
| `$483F` | — | `core/sim/__init__.py`:379 |
| `$48F7` | — | `core/constants.py`:1014<br>`core/sim/orders.py`:648 |
| `$48FC` | — | `core/constants.py`:988<br>`core/sim/orders.py`:270, 548 |
| `$4911` | — | `core/sim/orders.py`:291 |
| `$4940` | `resolve_attack` | `core/alien.py`:848<br>`core/constants.py`:238, 239, 280, 637<br>`core/menu.py`:442, 628<br>`core/orders.py`:61<br>`core/sim/orders.py`:291, 320, 478 |
| `$4976` | — | `core/constants.py`:254, 287 |
| `$497A` | — | `core/constants.py`:262, 502 |
| `$4980` | — | `core/constants.py`:285 |
| `$498D` | — | `core/constants.py`:256<br>`core/items.py`:62 |
| `$49A2` | — | `core/constants.py`:274 |
| `$49A8` | — | `core/constants.py`:274 |
| `$49AB` | — | `core/constants.py`:271 |
| `$49B5` | — | `core/constants.py`:262, 500, 501<br>`core/items.py`:107 |
| `$49C2` | — | `core/constants.py`:271 |
| `$49EB` | — | `core/constants.py`:311 |
| `$49F2` | — | `core/constants.py`:249 |
| `$49F6` | — | `core/constants.py`:257 |
| `$49FB` | — | `core/constants.py`:285 |
| `$4A87` | — | `core/constants.py`:311 |
| `$4A95` | — | `core/constants.py`:324 |
| `$4AF0` | — | `core/constants.py`:312 |
| `$4AFD` | — | `core/constants.py`:323 |
| `$4B22` | — | `core/items.py`:106 |
| `$4B37` | `tbl_weapon_charge` | `core/constants.py`:479, 490, 492<br>`core/items.py`:20, 102<br>`core/menu.py`:732<br>`core/sim/orders.py`:302<br>`core/sim/specials.py`:195, 198 |
| `$4B47` | — | `core/constants.py`:478, 479, 495, 496, 497 |
| `$4B5A` | — | `core/menu.py`:732<br>`core/sim/specials.py`:197 |
| `$4BEF` | `var_attack_item` | `core/constants.py`:240<br>`core/menu.py`:858, 860<br>`core/nostromo.py`:95 |
| `$4C9C` | — | `core/alien.py`:605 |
| `$4CB3` | — | `core/alien.py`:272<br>`core/sim/__init__.py`:157 |
| `$4CB8` | — | `core/alien.py`:592, 605 |
| `$4CC3` | — | `core/sim/__init__.py`:156, 900 |
| `$4CC9` | — | `render/play.py`:521 |
| `$4CE2` | — | `render/play.py`:521, 526 |
| `$4CE8` | `raise_crowd_fear` | `core/constants.py`:78, 388<br>`core/sim/__init__.py`:744 |
| `$4CF5` | — | `core/constants.py`:904 |
| `$4CF9` | — | `core/constants.py`:378 |
| `$4D02` | — | `audio/sfx.py`:307<br>`core/constants.py`:666<br>`render/play.py`:113 |
| `$4D03` | — | `audio/sfx.py`:167<br>`core/sim/__init__.py`:961<br>`render/audio.py`:120<br>`render/pygame_app.py`:473 |
| `$4D04` | — | `render/play.py`:147, 161 |
| `$4D05` | — | `render/play.py`:147, 161 |
| `$4D06` | — | `render/play.py`:148, 163 |
| `$4D07` | — | `render/play.py`:148, 163 |
| `$4D08` | `irq_handler` | `audio/intro.py`:5, 6, 32, 59, 142<br>`render/pygame_app.py`:336 |
| `$4D11` | — | `audio/intro.py`:13 |
| `$4D19` | `game_tick_dispatch` | `core/constants.py`:30<br>`render/pygame_app.py`:330, 343 |
| `$4D2F` | — | `render/pygame_app.py`:332 |
| `$4D37` | — | `audio/intro.py`:27<br>`audio/sfx.py`:306<br>`core/constants.py`:674 |
| `$4D47` | — | `audio/sfx.py`:192 |
| `$4D58` | `irq_raster_split` | `audio/intro.py`:9<br>`render/play.py`:10, 137, 146 |
| `$4D89` | — | `audio/intro.py`:11 |
| `$4DB8` | `init_a_raster_irq` | `audio/intro.py`:4, 31 |
| `$4DD7` | — | `audio/intro.py`:27<br>`audio/sfx.py`:167, 306<br>`render/audio.py`:14, 119<br>`render/pygame_app.py`:473 |
| `$4DF0` | `init_sid_and_clear` | `audio/sfx.py`:155, 182 |
| `$4DF2` | — | `audio/sfx.py`:183 |
| `$4DF7` | — | `audio/sfx.py`:156 |
| `$4DFA` | — | `audio/sfx.py`:184 |
| `$4E01` | — | `audio/sfx.py`:157 |
| `$4E16` | `fear_alert` | `audio/sfx.py`:202<br>`core/constants.py`:87, 666, 682<br>`core/crew.py`:182<br>`core/orders.py`:12<br>`core/sim/__init__.py`:359<br>`core/sound.py`:37<br>`render/audio.py`:12, 88, 151<br>`render/play.py`:113<br>`render/pygame_app.py`:469 |
| `$4E1D` | — | `audio/sfx.py`:195 |
| `$4E22` | — | `audio/sfx.py`:191 |
| `$4E2F` | — | `audio/sfx.py`:195 |
| `$4E38` | — | `audio/sfx.py`:195 |
| `$4E3D` | — | `audio/sfx.py`:195 |
| `$4E42` | `sfx_blip_a` | `audio/sfx.py`:93<br>`core/sound.py`:61<br>`render/audio.py`:195, 205 |
| `$4E5C` | `sfx_blip_b` | `audio/sfx.py`:103<br>`core/sound.py`:61<br>`render/audio.py`:195, 205 |
| `$4E76` | `irq_alt_handler` | `audio/sfx.py`:265<br>`audio/sid.py`:322<br>`render/audio.py`:226 |
| `$4E87` | `sub_4e87` | `render/play.py`:10, 137, 140 |
| `$4E8E` | — | `render/pygame_app.py`:317, 323 |
| `$4ED4` | — | `render/play.py`:13, 103, 105, 1236 |
| `$4EDC` | `tbl_alien_anim` | `render/play.py`:166<br>`render/pygame_app.py`:305, 329 |
| `$4EE8` | `update_1` | `render/play.py`:158<br>`render/pygame_app.py`:305 |
| `$4EEE` | — | `render/play.py`:167<br>`render/pygame_app.py`:328 |
| `$4EFB` | — | `render/play.py`:167 |
| `$4F19` | `update_2` | `render/play.py`:99 |
| `$4F25` | — | `render/play.py`:564, 572 |
| `$4F33` | — | `render/play.py`:99, 931 |
| `$4F38` | — | `render/play.py`:103, 115, 1239 |
| `$4F3D` | — | `render/play.py`:115, 119 |
| `$4F3F` | — | `render/play.py`:1239 |
| `$4F48` | — | `render/play.py`:103 |
| `$4F52` | `update_3` | `render/play.py`:181 |
| `$4F57` | — | `render/play.py`:187 |
| `$4F5C` | — | `render/play.py`:1275 |
| `$4F5E` | — | `render/pygame_app.py`:284 |
| `$4F6E` | — | `render/play.py`:1282 |
| `$4F78` | — | `render/pygame_app.py`:284 |
| `$4F7A` | — | `render/play.py`:170<br>`render/pygame_app.py`:286 |
| `$4F90` | `begin_active_play` | `audio/sfx.py`:122<br>`audio/sid.py`:324<br>`render/audio.py`:225 |
| `$4F92` | — | `core/menu.py`:640 |
| `$4F95` | — | `render/play.py`:159 |
| `$4FA2` | — | `render/pygame_app.py`:288 |
| `$4FCB` | `update_4` | `render/layout.py`:30<br>`render/play.py`:9, 122, 1194 |
| `$4FDB` | — | `render/play.py`:121 |
| `$4FF1` | `maybe_clear_64ba` | `render/pygame_app.py`:293 |
| `$4FF4` | — | `render/play.py`:1257 |
| `$4FFB` | — | `render/play.py`:1257 |
| `$4FFC` | — | `render/play.py`:1254 |
| `$5000` | — | `audio/sfx.py`:103<br>`core/sim/__init__.py`:938 |
| `$501E` | `pause_clear_active` | `audio/sfx.py`:24, 72<br>`core/menu.py`:641 |
| `$5049` | `sub_5049` | `core/constants.py`:811 |
| `$506E` | — | `core/constants.py`:814 |
| `$5071` | — | `core/modes.py`:37 |
| `$5074` | — | `core/crew.py`:299<br>`core/sim/__init__.py`:183 |
| `$5077` | — | `core/crew.py`:299, 327<br>`core/sim/__init__.py`:92, 183 |
| `$507A` | — | `core/modes.py`:61<br>`core/sim/__init__.py`:215 |
| `$507E` | — | `core/constants.py`:815 |
| `$5086` | — | `core/modes.py`:61<br>`core/sim/__init__.py`:215 |
| `$5089` | — | `core/opening_name.py`:7 |
| `$5092` | — | `render/frontend.py`:49, 1224, 1242 |
| `$509C` | — | `core/opening_name.py`:7 |
| `$50A0` | `show_death_msg` | `render/frontend.py`:49, 1243 |
| `$50AB` | — | `core/constants.py`:817<br>`core/crew.py`:327 |
| `$50B3` | — | `core/constants.py`:984 |
| `$50B5` | — | `core/crew.py`:327 |
| `$50B8` | — | `core/constants.py`:743 |
| `$50BB` | — | `core/constants.py`:743 |
| `$50BF` | — | `core/opening_name.py`:11 |
| `$50EC` | — | `core/constants.py`:814, 820, 823<br>`core/crew.py`:313<br>`core/modes.py`:37, 84<br>`core/sim/__init__.py`:187 |
| `$50FC` | — | `core/constants.py`:815, 827, 834<br>`core/modes.py`:61 |
| `$510C` | — | `core/crew.py`:314<br>`core/sim/__init__.py`:188 |
| `$511C` | `menu_option_dispatch` | `render/play.py`:530, 535 |
| `$5134` | — | `render/play.py`:564<br>`render/pygame_app.py`:1201 |
| `$513B` | — | `render/play.py`:564<br>`render/pygame_app.py`:1201 |
| `$5156` | `resolve_char_move` | `core/constants.py`:397<br>`core/crew.py`:125 |
| `$5168` | — | `core/constants.py`:850 |
| `$5170` | — | `core/constants.py`:876, 890<br>`core/sim/__init__.py`:358, 600, 650, 654 |
| `$517A` | — | `core/constants.py`:881<br>`core/sim/__init__.py`:607, 647 |
| `$5182` | — | `core/constants.py`:883<br>`core/sim/__init__.py`:609 |
| `$5193` | — | `core/sim/orders.py`:194 |
| `$519B` | — | `core/sim/orders.py`:194 |
| `$51E7` | — | `core/constants.py`:884<br>`core/sim/__init__.py`:610, 663 |
| `$51EC` | — | `core/constants.py`:876 |
| `$51F4` | — | `core/sim/__init__.py`:615, 626, 629, 663 |
| `$5200` | — | `core/sim/__init__.py`:636, 638 |
| `$5202` | — | `core/sim/__init__.py`:636, 638 |
| `$5203` | `char_wander` | `core/alien.py`:95, 237<br>`core/constants.py`:88<br>`core/orders.py`:13<br>`core/sim/__init__.py`:550, 598, 639, 666, 904, 908 |
| `$5205` | — | `core/sim/__init__.py`:667, 684 |
| `$5214` | — | `core/alien.py`:97<br>`core/sim/__init__.py`:623 |
| `$521B` | — | `core/sim/__init__.py`:669 |
| `$521E` | — | `core/sim/__init__.py`:689 |
| `$5221` | — | `core/constants.py`:891<br>`core/sim/__init__.py`:670, 685 |
| `$522B` | — | `core/sim/__init__.py`:666 |
| `$524F` | — | `core/alien.py`:97<br>`core/sim/__init__.py`:623 |
| `$5252` | — | `core/constants.py`:95<br>`core/sim/__init__.py`:665 |
| `$5262` | — | `core/sim/__init__.py`:600 |
| `$5265` | — | `core/constants.py`:850<br>`core/sim/__init__.py`:416, 495, 916 |
| `$526A` | — | `core/constants.py`:871<br>`core/sim/__init__.py`:425 |
| `$526D` | — | `core/sim/__init__.py`:917 |
| `$526F` | — | `core/sim/__init__.py`:919 |
| `$5272` | — | `core/sim/__init__.py`:419, 917 |
| `$527A` | — | `core/sim/__init__.py`:419 |
| `$528A` | — | `core/constants.py`:95, 864<br>`core/sim/__init__.py`:420 |
| `$5294` | — | `core/sim/orders.py`:130 |
| `$5299` | — | `core/sim/orders.py`:130 |
| `$52A4` | — | `core/constants.py`:96, 866, 867<br>`core/sim/__init__.py`:438 |
| `$52A7` | — | `core/constants.py`:873 |
| `$52C0` | — | `core/constants.py`:87, 415, 422<br>`core/crew.py`:182, 291<br>`core/orders.py`:12 |
| `$52C3` | — | `core/constants.py`:874 |
| `$52CA` | — | `core/sim/__init__.py`:461 |
| `$52D4` | — | `core/sim/__init__.py`:464<br>`core/state.py`:112 |
| `$52D7` | — | `core/constants.py`:870<br>`core/sim/__init__.py`:592<br>`core/state.py`:111, 203 |
| `$52DA` | — | `core/constants.py`:866, 871<br>`core/sim/__init__.py`:438, 467, 470<br>`core/state.py`:113, 185<br>`render/play.py`:607 |
| `$52E3` | — | `core/constants.py`:96 |
| `$52F1` | — | `core/constants.py`:872<br>`core/sim/__init__.py`:425, 493, 499, 915, 919 |
| `$52FC` | — | `core/sim/__init__.py`:568 |
| `$5306` | — | `core/sim/__init__.py`:568 |
| `$5309` | — | `core/sim/__init__.py`:504, 505, 534, 559 |
| `$5311` | — | `core/sim/__init__.py`:507 |
| `$5313` | — | `core/sim/__init__.py`:581 |
| `$5318` | — | `core/sim/__init__.py`:524, 583 |
| `$531D` | — | `core/sim/__init__.py`:585 |
| `$5324` | — | `core/sim/__init__.py`:520, 587 |
| `$5329` | — | `core/sim/__init__.py`:589 |
| `$5339` | — | `core/sim/__init__.py`:595 |
| `$533F` | — | `core/constants.py`:840 |
| `$5345` | — | `core/constants.py`:839<br>`core/sim/__init__.py`:515, 590, 920 |
| `$5354` | `alien_wound_crew` | `core/alien.py`:764<br>`core/constants.py`:406, 414, 454<br>`core/sim/__init__.py`:590<br>`render/audio.py`:207 |
| `$53E3` | — | `core/sim/__init__.py`:514 |
| `$53E4` | — | `core/alien.py`:371 |
| `$5439` | — | `core/constants.py`:837<br>`core/sim/__init__.py`:497, 912<br>`core/sim/orders.py`:290<br>`core/state.py`:116 |
| `$5459` | — | `core/constants.py`:846<br>`core/sim/__init__.py`:358, 497, 522 |
| `$5460` | — | `core/constants.py`:847 |
| `$546D` | — | `core/constants.py`:838 |
| `$5473` | — | `core/constants.py`:534 |
| `$547C` | — | `core/constants.py`:534 |
| `$5485` | `txt_structural_damage` | `render/play.py`:1041 |
| `$54A3` | — | `core/alien.py`:356, 358<br>`core/constants.py`:545, 550, 629<br>`core/state.py`:160, 167 |
| `$54C6` | — | `core/constants.py`:534, 599, 600 |
| `$555C` | — | `core/constants.py`:573, 579, 599 |
| `$5578` | — | `core/constants.py`:574, 579, 600 |
| `$5580` | — | `core/constants.py`:518 |
| `$5587` | `damage_room_b` | `core/alien.py`:320, 353<br>`core/constants.py`:509, 531<br>`core/sim/orders.py`:456<br>`core/state.py`:151, 165<br>`render/play.py`:1040 |
| `$558C` | — | `core/constants.py`:510, 513 |
| `$558F` | — | `core/constants.py`:327, 344, 367 |
| `$5593` | — | `core/alien.py`:327 |
| `$5594` | — | `core/constants.py`:340, 514, 527 |
| `$5598` | — | `core/alien.py`:329 |
| `$559E` | — | `core/alien.py`:322, 340<br>`core/constants.py`:517 |
| `$55A6` | — | `core/alien.py`:354 |
| `$55A9` | — | `core/constants.py`:347, 628<br>`core/menu.py`:51, 724 |
| `$55AD` | — | `core/constants.py`:347, 629<br>`core/menu.py`:51 |
| `$55B1` | — | `core/alien.py`:332, 345, 357, 373<br>`core/constants.py`:348, 523, 628<br>`core/menu.py`:738<br>`core/state.py`:159 |
| `$55B3` | — | `core/menu.py`:724 |
| `$55C1` | — | `core/alien.py`:355<br>`core/constants.py`:533<br>`core/state.py`:166<br>`render/play.py`:1040 |
| `$55C4` | — | `core/alien.py`:368 |
| `$55C9` | `draw_damage_warning` | `core/constants.py`:569<br>`render/play.py`:595, 909, 1025 |
| `$55F2` | — | `core/alien.py`:371<br>`core/constants.py`:539 |
| `$561C` | `delay_long` | `core/constants.py`:583, 588, 772<br>`core/sim/specials.py`:177<br>`core/state.py`:171 |
| `$561E` | `delay` | `core/constants.py`:731 |
| `$5626` | — | `core/constants.py`:591, 594<br>`core/sim/specials.py`:179<br>`core/state.py`:176<br>`render/play.py`:638 |
| `$5628` | — | `core/constants.py`:591<br>`core/sim/specials.py`:179<br>`core/state.py`:176<br>`render/play.py`:638 |
| `$5658` | — | `core/alien.py`:329<br>`core/constants.py`:330, 514, 518 |
| `$565C` | — | `core/sim/__init__.py`:1030<br>`core/state.py`:218 |
| `$565F` | — | `core/constants.py`:329<br>`core/sim/__init__.py`:1011 |
| `$5667` | — | `core/constants.py`:528 |
| `$5669` | — | `core/constants.py`:329 |
| `$5684` | `mainloop_sub_5684` | `core/constants.py`:353<br>`core/sim/__init__.py`:975 |
| `$5690` | — | `core/constants.py`:356 |
| `$56B4` | `guard_target_alive` | `core/menu.py`:44, 560<br>`core/sim/specials.py`:93 |
| `$56B7` | — | `core/menu.py`:559, 668, 714, 735, 762 |
| `$56BD` | — | `core/menu.py`:561 |
| `$56C1` | — | `core/menu.py`:544<br>`core/sim/specials.py`:217 |
| `$56C9` | — | `core/menu.py`:755 |
| `$56CD` | — | `core/menu.py`:756 |
| `$56D2` | — | `core/menu.py`:758 |
| `$56DF` | — | `core/menu.py`:756 |
| `$56FF` | — | `core/menu.py`:710 |
| `$5751` | — | `core/menu.py`:661, 677 |
| `$5752` | — | `core/menu.py`:661, 677 |
| `$5753` | — | `core/alien.py`:315, 357, 373<br>`core/constants.py`:348, 524, 628, 631, 632<br>`core/menu.py`:44, 544, 559, 691, 727, 737<br>`core/sim/orders.py`:453<br>`core/sim/specials.py`:9, 202, 216, 221, 252<br>`core/special_options.py`:42<br>`core/state.py`:158 |
| `$5776` | — | `core/menu.py`:43, 709, 754<br>`core/nostromo.py`:85 |
| `$5799` | — | `core/menu.py`:674, 700, 712, 767, 778 |
| `$57A0` | `tbl_specials_menu` | `core/menu.py`:523<br>`core/sim/specials.py`:114<br>`core/special_options.py`:22<br>`render/pygame_app.py`:227 |
| `$57B6` | — | `core/menu.py`:523<br>`core/sim/specials.py`:3 |
| `$57D4` | — | `core/crew.py`:121<br>`core/menu.py`:745<br>`core/special_options.py`:80<br>`core/state.py`:49 |
| `$5839` | — | `core/menu.py`:690<br>`core/sim/specials.py`:85, 219<br>`core/special_options.py`:42 |
| `$583F` | — | `core/sim/specials.py`:83 |
| `$5842` | — | `core/sim/specials.py`:100, 112 |
| `$5847` | — | `core/sim/specials.py`:110 |
| `$585E` | — | `core/constants.py`:687, 696, 701<br>`core/sim/specials.py`:159<br>`core/state.py`:234 |
| `$5869` | — | `core/menu.py`:538<br>`core/special_options.py`:80 |
| `$586D` | — | `core/sim/specials.py`:268 |
| `$5883` | — | `core/menu.py`:539<br>`core/special_options.py`:80 |
| `$5888` | — | `core/sim/specials.py`:89, 91 |
| `$5889` | — | `core/constants.py`:506<br>`core/menu.py`:535, 537, 726<br>`core/sim/orders.py`:450<br>`core/sim/specials.py`:185, 221<br>`core/special_options.py`:76, 78<br>`core/state.py`:154 |
| `$5899` | — | `core/constants.py`:489 |
| `$58CA` | — | `core/sim/orders.py`:471 |
| `$58CF` | — | `core/constants.py`:630<br>`core/sim/specials.py`:252<br>`core/state.py`:161 |
| `$58D2` | — | `core/sim/orders.py`:471 |
| `$58D5` | — | `core/sim/specials.py`:253 |
| `$58E3` | `set_result_win` | `core/constants.py`:687 |
| `$58E5` | — | `core/scoring.py`:52<br>`core/sim/specials.py`:151<br>`core/state.py`:208 |
| `$58E8` | — | `core/constants.py`:687, 699 |
| `$58ED` | — | `core/constants.py`:700 |
| `$58F6` | `clear_result_flag` | `core/sim/specials.py`:168<br>`render/play.py`:631 |
| `$58FE` | — | `render/play.py`:632 |
| `$5900` | — | `render/play.py`:632 |
| `$5904` | `blowlock_sfx` | `app.py`:87<br>`audio/sfx.py`:112<br>`core/sim/specials.py`:131, 133, 268<br>`core/sound.py`:66 |
| `$5915` | — | `core/sim/specials.py`:133 |
| `$591F` | — | `core/sim/specials.py`:134, 256 |
| `$5922` | — | `core/sim/specials.py`:258 |
| `$592E` | — | `core/sim/specials.py`:134 |
| `$5931` | — | `core/sim/specials.py`:258 |
| `$5939` | `guard_target_is_player` | `core/constants.py`:841<br>`core/menu.py`:693<br>`core/sim/specials.py`:435<br>`core/special_options.py`:40 |
| `$593C` | — | `core/constants.py`:842<br>`core/sim/specials.py`:142 |
| `$5950` | — | `core/constants.py`:581, 587<br>`core/menu.py`:540<br>`core/sim/orders.py`:454<br>`core/sim/specials.py`:204, 253<br>`core/special_options.py`:81<br>`core/state.py`:173 |
| `$595A` | `check_tracker` | `audio/sfx.py`:32 |
| `$599E` | `stow_char` | `core/alien.py`:805<br>`core/state.py`:105 |
| `$59A7` | `restore_stowed_char` | `core/alien.py`:817, 820<br>`core/sim/__init__.py`:889<br>`core/state.py`:106 |
| `$59AE` | — | `core/alien.py`:821 |
| `$59B9` | — | `core/alien.py`:821, 834 |
| `$59C3` | — | `core/alien.py`:823 |
| `$59C8` | — | `core/alien.py`:823 |
| `$59D5` | — | `core/constants.py`:400 |
| `$5A0D` | — | `core/constants.py`:376, 386<br>`core/sim/__init__.py`:167, 781<br>`core/sim/protocol.py`:44 |
| `$5A26` | `mainloop_sub_5a26` | `core/constants.py`:566<br>`core/state.py`:209<br>`render/play.py`:617, 1023 |
| `$5A2C` | — | `render/play.py`:621 |
| `$5A34` | — | `core/constants.py`:687, 688<br>`core/state.py`:232 |
| `$5A3B` | — | `core/constants.py`:700 |
| `$5A3E` | — | `core/constants.py`:609, 703<br>`core/special_options.py`:63 |
| `$5A43` | — | `core/constants.py`:613<br>`core/sim/__init__.py`:1003<br>`core/state.py`:219 |
| `$5A46` | — | `core/constants.py`:571, 601, 709 |
| `$5A58` | — | `core/constants.py`:572 |
| `$5A63` | — | `core/constants.py`:609 |
| `$5A66` | — | `core/constants.py`:687, 703 |
| `$5A6A` | `blowlock_vent` | `core/constants.py`:930<br>`core/menu.py`:661<br>`core/sim/specials.py`:274 |
| `$5A6C` | — | `core/constants.py`:933<br>`core/sim/specials.py`:301 |
| `$5A7E` | — | `core/sim/specials.py`:306 |
| `$5A80` | — | `core/constants.py`:936<br>`core/sim/specials.py`:312 |
| `$5A8D` | — | `core/constants.py`:934<br>`core/sim/specials.py`:313 |
| `$5A92` | — | `core/constants.py`:934 |
| `$5A9E` | — | `core/constants.py`:935<br>`core/sim/specials.py`:315 |
| `$5ABD` | — | `core/sim/specials.py`:306 |
| `$5ABF` | — | `core/constants.py`:937<br>`core/sim/specials.py`:319, 325 |
| `$5ACF` | — | `core/constants.py`:938, 943<br>`core/sim/specials.py`:326 |
| `$5AD3` | — | `core/sim/specials.py`:319 |
| `$5AD7` | — | `core/menu.py`:662<br>`core/sim/specials.py`:278 |
| `$5ADD` | `alien_maybe_hide` | `core/constants.py`:939<br>`core/sim/specials.py`:290 |
| `$5AE0` | — | `core/sim/specials.py`:330 |
| `$5AE5` | — | `core/sim/specials.py`:354 |
| `$5AEE` | — | `core/sim/specials.py`:331, 349 |
| `$5AF6` | — | `core/constants.py`:946<br>`core/sim/specials.py`:352 |
| `$5AFB` | — | `core/constants.py`:948<br>`core/sim/specials.py`:351 |
| `$5B00` | — | `core/constants.py`:945<br>`core/sim/specials.py`:331 |
| `$5B04` | `apply_blowlock` | `core/constants.py`:931<br>`core/menu.py`:660<br>`core/sim/specials.py`:256<br>`core/special_options.py`:29 |
| `$5B1F` | `check_mother_refuses` | `core/sim/specials.py`:361, 392<br>`core/state.py`:99 |
| `$5B3E` | — | `core/sim/specials.py`:415 |
| `$5B42` | — | `core/sim/specials.py`:415 |
| `$5B4C` | — | `core/sim/specials.py`:422 |
| `$5B56` | `alien_arrive` | `core/alien.py`:651<br>`core/sim/__init__.py`:1033, 1055 |
| `$5B5B` | — | `core/menu.py`:964<br>`core/sim/__init__.py`:1038, 1057 |
| `$5B5F` | — | `core/sim/__init__.py`:1040, 1059 |
| `$5B64` | — | `core/sim/__init__.py`:1040, 1059 |
| `$5B6C` | — | `core/crew.py`:106<br>`core/sim/__init__.py`:1041, 1061 |
| `$5B76` | — | `core/sim/__init__.py`:1045 |
| `$5B7C` | — | `core/sim/__init__.py`:1043, 1063 |
| `$5B7E` | — | `core/sim/__init__.py`:1033, 1055 |
| `$5B80` | — | `core/constants.py`:581, 585<br>`core/sim/specials.py`:364, 390<br>`core/state.py`:172 |
| `$5B95` | `show_mother_refuses` | `core/menu.py`:531<br>`core/sim/specials.py`:360 |
| `$5B9E` | — | `core/sim/specials.py`:360 |
| `$5BCB` | — | `core/sim/specials.py`:379 |
| `$5BD3` | — | `core/sim/specials.py`:378 |
| `$5BD8` | — | `core/sim/specials.py`:378, 387 |
| `$5BDD` | — | `core/sim/specials.py`:379 |
| `$5BE7` | `clear_line_07c0` | `core/constants.py`:583<br>`core/sim/__init__.py`:858 |
| `$5C18` | — | `core/sim/specials.py`:424<br>`core/state.py`:223 |
| `$5C33` | — | `core/constants.py`:581, 586<br>`core/sim/specials.py`:366, 407<br>`core/state.py`:173 |
| `$5C42` | `animate_fill_row` | `render/endscreen.py`:62, 68 |
| `$5C55` | — | `render/endscreen.py`:60, 83, 104 |
| `$5C63` | — | `render/endscreen.py`:62, 106 |
| `$5C6A` | — | `render/endscreen.py`:176 |
| `$5C70` | — | `render/endscreen.py`:108 |
| `$5C77` | — | `render/endscreen.py`:109 |
| `$5C90` | — | `render/endscreen.py`:112 |
| `$5C93` | — | `render/endscreen.py`:113 |
| `$5C98` | — | `render/endscreen.py`:114 |
| `$5CA8` | — | `render/endscreen.py`:119 |
| `$5CB4` | — | `render/endscreen.py`:120 |
| `$5CBB` | — | `render/endscreen.py`:121 |
| `$5CD4` | — | `render/endscreen.py`:124 |
| `$5CD7` | — | `render/endscreen.py`:125 |
| `$5CEA` | `anim_sound_tick` | `render/endscreen.py`:136 |
| `$5D11` | — | `render/endscreen.py`:150<br>`render/frontend.py`:309 |
| `$5D17` | `hull_breach` | `core/state.py`:215<br>`render/endscreen.py`:56, 144, 211 |
| `$5D25` | — | `render/endscreen.py`:56 |
| `$5D48` | — | `render/endscreen.py`:158 |
| `$5D6C` | — | `render/endscreen.py`:58 |
| `$5DAD` | — | `core/state.py`:225 |
| `$5DC6` | — | `core/sim/__init__.py`:1026<br>`core/state.py`:209 |
| `$5DC8` | — | `core/scoring.py`:52 |
| `$5DCE` | — | `render/endscreen.py`:213 |
| `$5DDB` | — | `render/frontend.py`:128 |
| `$5DEB` | `init_c` | `render/frontend.py`:125, 554<br>`render/pygame_app.py`:322 |
| `$5E4A` | — | `render/frontend.py`:211 |
| `$5E67` | — | `render/frontend.py`:211 |
| `$5E74` | — | `core/flow.py`:361<br>`render/frontend.py`:202, 554 |
| `$5E81` | — | `core/constants.py`:735 |
| `$5E8E` | — | `core/constants.py`:736 |
| `$5E90` | — | `core/constants.py`:772<br>`core/flow.py`:188<br>`render/frontend.py`:566 |
| `$5E96` | — | `core/constants.py`:736 |
| `$5E9E` | — | `core/constants.py`:736 |
| `$5EA6` | — | `core/constants.py`:736 |
| `$5EAE` | — | `core/constants.py`:736 |
| `$5EB6` | — | `core/constants.py`:737 |
| `$5EB7` | — | `core/constants.py`:772 |
| `$5EB9` | — | `core/constants.py`:737 |
| `$5EBC` | — | `core/constants.py`:737 |
| `$5EC0` | — | `render/frontend.py`:240, 241 |
| `$5ECE` | `main_dispatch` | `render/layout.py`:42<br>`render/pygame_app.py`:313 |
| `$5EEF` | — | `render/frontend.py`:1179<br>`render/layout.py`:45 |
| `$5EF7` | — | `render/layout.py`:42 |
| `$5F36` | — | `core/flow.py`:323<br>`render/pygame_app.py`:869, 1007 |
| `$5F3F` | — | `core/flow.py`:342 |
| `$5F4E` | — | `core/sim/__init__.py`:244 |
| `$5F51` | — | `core/flow.py`:342 |
| `$5F59` | `txt_game_selection` | `render/pygame_app.py`:882 |
| `$5F70` | — | `core/flow.py`:123 |
| `$5F87` | — | `core/flow.py`:123 |
| `$5FC3` | `sub_screen_setup` | `render/frontend.py`:1172, 1202, 1230 |
| `$604F` | `sub_604f` | `core/constants.py`:796<br>`core/gamedata_snapshot.py`:45<br>`core/nostromo.py`:161<br>`core/sim/__init__.py`:224, 241, 243 |
| `$6051` | — | `core/sim/__init__.py`:222 |
| `$6057` | — | `core/sim/__init__.py`:222 |
| `$605A` | — | `core/sim/__init__.py`:289 |
| `$605F` | — | `core/sim/__init__.py`:289 |
| `$6062` | — | `core/constants.py`:831<br>`core/sim/__init__.py`:245 |
| `$6064` | — | `core/modes.py`:38 |
| `$6067` | — | `core/sim/__init__.py`:246 |
| `$6069` | — | `core/constants.py`:831 |
| `$608C` | — | `core/sim/__init__.py`:247 |
| `$6093` | — | `core/sim/__init__.py`:248 |
| `$609A` | — | `core/crew.py`:104<br>`core/sim/__init__.py`:248 |
| `$60A1` | — | `core/sim/__init__.py`:249 |
| `$60A8` | `var_music_mode` | `audio/intro.py`:10, 13, 14, 23, 61<br>`render/audio.py`:47<br>`render/pygame_app.py`:434 |
| `$60A9` | `select_outcome` | `core/scoring.py`:5, 38<br>`render/endscreen.py`:10, 180<br>`screens/ending.py`:8, 20 |
| `$60AE` | — | `core/scoring.py`:20, 53<br>`core/state.py`:210<br>`screens/ending.py`:44 |
| `$60D0` | — | `core/scoring.py`:40<br>`render/endscreen.py`:189<br>`screens/ending.py`:44 |
| `$60D8` | — | `core/scoring.py`:49<br>`core/sim/__init__.py`:94<br>`render/endscreen.py`:198, 244 |
| `$60DF` | — | `core/scoring.py`:45, 46, 79, 85, 113 |
| `$60F9` | — | `core/scoring.py`:42 |
| `$611C` | — | `core/scoring.py`:44, 80, 86, 116 |
| `$6130` | — | `core/constants.py`:843 |
| `$614F` | — | `render/endscreen.py`:248 |
| `$6166` | — | `render/endscreen.py`:205, 257<br>`screens/ending.py`:81 |
| `$617F` | — | `screens/ending.py`:20 |
| `$61A5` | — | `core/constants.py`:845<br>`core/scoring.py`:7, 126 |
| `$61B0` | — | `core/scoring.py`:8, 131 |
| `$61BB` | — | `core/scoring.py`:66 |
| `$61C6` | — | `core/scoring.py`:15, 134 |
| `$61CA` | — | `core/scoring.py`:67 |
| `$61E2` | — | `core/crew.py`:236 |
| `$61E7` | — | `render/endscreen.py`:263 |
| `$61F6` | — | `core/crew.py`:240<br>`core/scoring.py`:136 |
| `$61FA` | — | `core/scoring.py`:68 |
| `$6204` | — | `screens/ending.py`:82 |
| `$6217` | — | `core/scoring.py`:7 |
| `$621D` | — | `core/scoring.py`:30, 74, 81 |
| `$6221` | — | `core/scoring.py`:138 |
| `$6229` | — | `core/state.py`:213<br>`render/endscreen.py`:197 |
| `$6231` | — | `core/scoring.py`:19 |
| `$6245` | — | `core/scoring.py`:70 |
| `$6249` | — | `core/scoring.py`:71 |
| `$624D` | — | `core/scoring.py`:25 |
| `$6251` | — | `core/scoring.py`:72 |
| `$6259` | — | `core/scoring.py`:26 |
| `$625D` | — | `core/scoring.py`:73 |
| `$6265` | — | `core/scoring.py`:27, 69, 92 |
| `$6269` | — | `core/alien.py`:310 |
| `$626A` | — | `core/scoring.py`:75 |
| `$626E` | — | `core/scoring.py`:28, 69, 94 |
| `$6278` | — | `core/scoring.py`:19, 28 |
| `$627B` | — | `core/scoring.py`:92 |
| `$6288` | — | `core/scoring.py`:31, 143 |
| `$62B5` | — | `core/scoring.py`:5, 31, 143 |
| `$62B6` | `draw_ending_survivor` | `render/endscreen.py`:234<br>`screens/ending.py`:33, 49, 69 |
| `$62D6` | — | `core/state.py`:211<br>`render/endscreen.py`:196<br>`screens/ending.py`:50 |
| `$62DC` | `draw_ending_lost` | `screens/ending.py`:33 |
| `$62EA` | `draw_ending_survivors` | `screens/ending.py`:33 |
| `$6300` | — | `core/state.py`:224 |
| `$6314` | `tbl_nostromo_endings` | `render/endscreen.py`:234<br>`screens/ending.py`:18, 50, 56, 69 |
| `$633C` | — | `screens/ending.py`:47, 54 |
| `$6359` | — | `screens/ending.py`:52, 55 |
| `$6372` | `txt_alien_dead` | `core/scoring.py`:43<br>`screens/ending.py`:26, 37 |
| `$6383` | `txt_eggs_unleashed` | `screens/ending.py`:29, 38 |
| `$63BA` | `txt_narcissus_returns` | `screens/ending.py`:27, 42 |
| `$63D8` | — | `screens/ending.py`:30, 43 |
| `$63E5` | — | `core/crew.py`:236, 238<br>`screens/ending.py`:60 |
| `$63EE` | — | `screens/ending.py`:61 |
| `$63F8` | `txt_competence_rating` | `core/scoring.py`:3<br>`screens/ending.py`:62 |
| `$640F` | `var_640f_score` | `core/scoring.py`:21, 24, 25, 26, 27, 28… |
| `$6411` | `var_competence_score` | `core/crew.py`:240<br>`core/scoring.py`:4, 10, 11, 13, 28, 43… |
| `$645E` | — | `render/endscreen.py`:278 |
| `$6467` | — | `render/endscreen.py`:278 |
| `$646F` | — | `core/flow.py`:360 |
| `$6475` | — | `render/endscreen.py`:277<br>`render/frontend.py`:180<br>`screens/ending.py`:63 |
| `$64A0` | `var_alien_active` | `core/alien.py`:308, 309, 608, 680 |
| `$64A3` | `var_alien_a3` | `core/alien.py`:679, 771<br>`core/constants.py`:439<br>`core/sim/__init__.py`:530 |
| `$64A4` | — | `core/alien.py`:780<br>`core/constants.py`:444, 448, 467 |
| `$64A6` | — | `core/alien.py`:780<br>`core/constants.py`:467 |
| `$64A9` | — | `core/sim/__init__.py`:783 |
| `$64B1` | `var_64b1` | `core/sim/__init__.py`:339 |
| `$64B4` | `var_alien_pursuit` | `core/alien.py`:272, 540, 544, 570, 591, 592…<br>`core/constants.py`:227, 293 |
| `$64B5` | `var_sound_value` | `audio/sfx.py`:191, 309 |
| `$64B6` | — | `audio/sfx.py`:150<br>`core/sim/__init__.py`:953<br>`core/sim/orders.py`:406<br>`core/sound.py`:32<br>`render/audio.py`:120, 121, 237<br>`render/frontend.py`:178<br>`render/play.py`:1101 |
| `$64B7` | `var_sound_tick` | `audio/sfx.py`:306, 307<br>`core/constants.py`:674 |
| `$64B8` | — | `render/audio.py`:119 |
| `$64B9` | — | `render/play.py`:147 |
| `$64BA` | — | `render/play.py`:1261<br>`render/pygame_app.py`:287, 443 |
| `$64BB` | `var_game_active` | `core/menu.py`:587, 588, 637, 639, 641<br>`core/sound.py`:61, 64<br>`render/audio.py`:195, 203, 204, 213, 227<br>`render/pygame_app.py`:446 |
| `$64BD` | — | `core/menu.py`:902 |
| `$64BE` | — | `core/menu.py`:864<br>`render/play.py`:1196 |
| `$64BF` | `var_anim_frame` | `render/play.py`:167<br>`render/pygame_app.py`:327, 328 |
| `$64C0` | — | `render/play.py`:171, 172 |
| `$64C1` | — | `render/play.py`:104, 115, 119 |
| `$64C2` | — | `core/constants.py`:814, 815, 817, 831<br>`core/modes.py`:36, 62<br>`core/opening_name.py`:9, 65<br>`core/sim/__init__.py`:187, 245 |
| `$64C3` | `var_special_char` | `core/alien.py`:765<br>`core/constants.py`:407, 455, 815, 825, 832, 833…<br>`core/modes.py`:59<br>`core/sim/__init__.py`:246, 510<br>`core/sim/specials.py`:379<br>`core/state.py`:195<br>`render/endscreen.py`:190<br>`screens/ending.py`:48 |
| `$64C4` | `tbl_char_state2` | `core/sim/__init__.py`:635 |
| `$64CC` | — | `core/constants.py`:870<br>`core/menu.py`:384<br>`core/sim/__init__.py`:425, 438, 464, 465, 496, 591…<br>`core/sim/specials.py`:379<br>`core/state.py`:111, 112, 117, 202 |
| `$64CE` | — | `core/constants.py`:353<br>`core/sim/__init__.py`:976 |
| `$64CF` | `var_result_flag` | `core/menu.py`:756<br>`core/scoring.py`:20, 36, 40, 44, 49, 50…<br>`core/sim/__init__.py`:1026<br>`core/sim/specials.py`:152, 168<br>`core/state.py`:207, 209<br>`render/endscreen.py`:186, 189, 196, 221<br>`render/play.py`:618, 621, 631<br>`screens/ending.py`:45, 50 |
| `$64D0` | — | `core/sim/orders.py`:454<br>`core/sim/specials.py`:203, 218, 222 |
| `$64D1` | — | `core/menu.py`:122, 383, 956<br>`core/sim/__init__.py`:1043, 1063 |
| `$64DC` | — | `core/alien.py`:807<br>`core/state.py`:103 |
| `$64DD` | — | `render/endscreen.py`:150 |
| `$64E0` | — | `render/endscreen.py`:62, 77, 78, 81, 82 |
| `$64E1` | — | `render/endscreen.py`:60, 62, 74, 76, 79, 80… |
| `$64E3` | `var_endgame_flag` | `core/scoring.py`:46<br>`core/sim/specials.py`:425<br>`core/state.py`:222<br>`render/endscreen.py`:200, 248 |
| `$64E5` | `var_64e5` | `core/menu.py`:819, 843, 903, 969<br>`core/orders.py`:55 |
| `$64E6` | `var_alien_target` | `core/alien.py`:517, 571, 652, 700<br>`core/constants.py`:173, 1001<br>`core/sim/orders.py`:194<br>`core/sim/specials.py`:336 |
| `$64EE` | `var_alien_move_timer` | `core/alien.py`:638, 685, 784<br>`core/constants.py`:54, 275, 891, 990, 999, 1004…<br>`core/sim/__init__.py`:151, 152, 160, 634, 670, 695…<br>`core/sim/orders.py`:90, 93, 162, 171, 195, 224…<br>`core/sim/protocol.py`:40<br>`core/sim/specials.py`:337 |
| `$64F7` | — | `core/menu.py`:415, 858<br>`core/nostromo.py`:91<br>`render/play.py`:204, 229, 273, 525 |
| `$64FB` | `var_current_char` | `core/alien.py`:802<br>`core/command_monitor.py`:146<br>`core/menu.py`:124, 380, 416, 561, 592, 643…<br>`core/sim/specials.py`:88, 189, 468, 501<br>`core/sound.py`:12<br>`render/audio.py`:10, 194<br>`render/frontend.py`:120<br>`render/play.py`:205, 230, 261, 332, 342, 407…<br>`render/pygame_app.py`:450<br>`screens/panels.py`:213 |
| `$64FC` | — | `core/menu.py`:496 |
| `$6500` | — | `core/ductmap.py`:49, 100, 104, 129 |
| `$6501` | `var_damage_guard` | `core/alien.py`:478, 729, 778, 820, 823<br>`core/command_monitor.py`:136<br>`core/constants.py`:295, 442, 854, 883, 936, 948…<br>`core/crew.py`:122<br>`core/menu.py`:246, 361, 418, 561<br>`core/sim/__init__.py`:290, 341, 363, 505, 511, 609<br>`core/sim/orders.py`:178, 186, 346, 592<br>`core/sim/specials.py`:280, 284, 338<br>`render/play.py`:208, 232, 237, 264, 268, 269… |
| `$6502` | — | `core/sim/__init__.py`:289 |
| `$6508` | — | `core/sim/__init__.py`:290 |
| `$6509` | — | `audio/sfx.py`:33, 34 |
| `$650C` | `tbl_char_pending` | `core/constants.py`:856, 859<br>`core/menu.py`:993<br>`core/sim/__init__.py`:624, 633, 668<br>`core/sim/orders.py`:90 |
| `$6514` | — | `render/pygame_app.py`:99 |
| `$6517` | `var_char_acted` | `core/sim/__init__.py`:955 |
| `$6518` | — | `core/constants.py`:912, 913<br>`core/sim/specials.py`:468, 470, 471 |
| `$651B` | — | `audio/sfx.py`:95, 337<br>`core/constants.py`:187<br>`core/sim/__init__.py`:937, 973 |
| `$651C` | `var_room_damage_stage` | `core/alien.py`:304, 321, 322, 330, 340, 353<br>`core/constants.py`:355, 363, 507, 513, 514, 520…<br>`core/sim/__init__.py`:1015<br>`core/sim/orders.py`:452, 457, 465, 471<br>`core/sim/specials.py`:201<br>`core/state.py`:150 |
| `$653F` | `var_room_damage` | `core/alien.py`:298, 304, 305, 310, 727<br>`core/constants.py`:149, 291, 299, 307, 356, 505<br>`core/scoring.py`:21<br>`core/sim/orders.py`:451, 458<br>`core/sim/specials.py`:208<br>`core/state.py`:145 |
| `$6562` | — | `core/alien.py`:278, 305, 661, 695, 728<br>`core/constants.py`:294<br>`core/menu.py`:582, 626<br>`core/sim/__init__.py`:476, 478, 479, 485, 507, 527…<br>`core/sound.py`:74<br>`render/audio.py`:126, 237<br>`render/play.py`:1101<br>`render/pygame_app.py`:446 |
| `$6563` | — | `core/alien.py`:268, 639, 652, 658, 682, 699…<br>`core/constants.py`:296 |
| `$6565` | — | `core/alien.py`:155<br>`core/constants.py`:645<br>`core/sim/orders.py`:341 |
| `$656A` | — | `core/alien.py`:155<br>`core/constants.py`:645<br>`core/sim/orders.py`:341 |
| `$656D` | — | `core/alien.py`:309 |
| `$656E` | — | `core/crew.py`:165, 166<br>`core/sim/orders.py`:539 |
| `$656F` | — | `core/sim/orders.py`:539 |
| `$6571` | `tbl_char_state3` | `audio/sfx.py`:196<br>`core/constants.py`:111, 667, 881, 884, 897, 972…<br>`core/crew.py`:64, 167, 190, 224<br>`core/menu.py`:387, 403<br>`core/sim/__init__.py`:317, 332, 349, 607, 610, 650<br>`core/sim/specials.py`:89<br>`render/play.py`:890 |
| `$6572` | — | `core/sim/__init__.py`:249 |
| `$6579` | `var_frame_divider` | `render/pygame_app.py`:332, 333 |
| `$657A` | — | `render/play.py`:122, 123, 1195 |
| `$657B` | — | `core/constants.py`:568, 571, 688, 690, 692, 693…<br>`core/menu.py`:758<br>`core/sim/specials.py`:160<br>`core/special_options.py`:63, 64<br>`core/state.py`:230, 237, 239, 241 |
| `$657C` | — | `core/constants.py`:567, 688, 700, 707, 708<br>`render/play.py`:626 |
| `$657D` | — | `core/constants.py`:942<br>`core/menu.py`:415<br>`core/sim/__init__.py`:804<br>`core/sim/specials.py`:295<br>`render/play.py`:204, 229, 236 |
| `$657E` | — | `core/sim/__init__.py`:149, 802, 809 |
| `$657F` | — | `core/constants.py`:654, 923<br>`core/sim/__init__.py`:800, 801<br>`core/sim/specials.py`:489 |
| `$6580` | — | `core/sim/orders.py`:357<br>`core/sim/specials.py`:474 |
| `$6581` | `var_alien_move_ticks` | `core/alien.py`:15, 489<br>`core/constants.py`:141, 171, 214, 215, 216 |
| `$6583` | — | `core/crew.py`:166 |
| `$6586` | `tbl_walk_ticks` | `core/constants.py`:1008, 1011<br>`core/crew.py`:163, 164, 170, 357, 358<br>`core/sim/__init__.py`:27<br>`core/sim/orders.py`:165 |
| `$6598` | `sub_beep` | `core/crew.py`:165 |
| `$659A` | — | `core/crew.py`:164 |
| `$65A9` | — | `core/alien.py`:308<br>`core/state.py`:118 |
| `$65B1` | — | `core/constants.py`:480 |
| `$65CB` | — | `audio/sfx.py`:167 |
| `$65FF` | — | `core/crew.py`:299, 341 |
| `$663D` | — | `audio/sfx.py`:86 |
| `$6667` | `place_alien_sprite` | `core/crew.py`:124<br>`core/sim/orders.py`:178<br>`render/play.py`:258, 259, 585, 957, 962 |
| `$666C` | — | `render/frontend.py`:120 |
| `$666F` | — | `render/play.py`:963 |
| `$6676` | — | `render/play.py`:964 |
| `$667C` | — | `render/play.py`:965 |
| `$7000` | — | `core/gamedata_snapshot.py`:69<br>`render/play.py`:756, 764<br>`screens/colours.py`:7<br>`screens/panels.py`:82, 88 |
| `$7013` | `start_game` | `core/flow.py`:342<br>`render/pygame_app.py`:94 |
| `$7027` | — | `core/state.py`:193<br>`render/play.py`:606 |
| `$702D` | `switch_to_gameplay_music` | `audio/intro.py`:23 |
| `$7046` | — | `render/play.py`:140 |
| `$7054` | — | `render/play.py`:628, 645 |
| `$7065` | — | `render/frontend.py`:1223 |
| `$706F` | — | `render/play.py`:765<br>`screens/panels.py`:53, 185 |
| `$7083` | — | `render/pygame_app.py`:288 |
| `$7112` | `init_ptr_menu2` | `core/gamedata_snapshot.py`:60<br>`render/play.py`:489 |
| `$7122` | `init_ptr_menu3` | `core/gamedata_snapshot.py`:60<br>`render/play.py`:489 |
| `$7132` | `init_menu_ptr` | `core/gamedata_snapshot.py`:60<br>`render/play.py`:489 |
| `$719D` | `main_loop` | `core/constants.py`:26, 48 |
| `$71AF` | — | `render/pygame_app.py`:895 |
| `$71B0` | `read_input` | `render/pygame_app.py`:893, 894 |
| `$7214` | — | `core/sim/__init__.py`:464, 465, 516, 592, 703<br>`core/state.py`:112, 113, 114 |
| `$7216` | `char_pump` | `core/sim/__init__.py`:693, 865 |
| `$7226` | — | `core/sim/orders.py`:170 |
| `$722E` | — | `core/sim/__init__.py`:699, 721 |
| `$7234` | — | `core/sim/__init__.py`:723 |
| `$7239` | — | `core/sim/__init__.py`:702 |
| `$723E` | — | `core/sim/__init__.py`:465<br>`core/state.py`:114 |
| `$729C` | — | `core/constants.py`:978<br>`core/crew.py`:126<br>`core/sim/orders.py`:635 |
| `$72EE` | — | `core/menu.py`:828 |
| `$72F9` | — | `core/sim/__init__.py`:935, 952<br>`core/sim/orders.py`:404 |
| `$72FC` | — | `core/sim/__init__.py`:952<br>`core/sim/orders.py`:404 |
| `$7302` | — | `core/sim/__init__.py`:889 |
| `$7305` | — | `core/constants.py`:931<br>`core/sim/__init__.py`:967<br>`core/sim/specials.py`:261 |
| `$7352` | — | `audio/sfx.py`:34 |
| `$7373` | — | `core/constants.py`:969<br>`core/sim/orders.py`:186, 592 |
| `$737E` | — | `core/sim/orders.py`:633 |
| `$7381` | — | `core/constants.py`:981<br>`core/sim/orders.py`:634 |
| `$738A` | — | `core/constants.py`:980 |
| `$738D` | — | `core/sim/orders.py`:633 |
| `$7392` | — | `core/constants.py`:969 |
| `$73C8` | `draw_deck_map` | `core/menu.py`:148, 149, 175 |
| `$73D0` | `draw_deck_map_body` | `render/deck_backdrop.py`:31 |
| `$7400` | — | `render/deck_backdrop.py`:32<br>`screens/panels.py`:99 |
| `$7423` | — | `render/deck_backdrop.py`:32 |
| `$7431` | — | `screens/panels.py`:100 |
| `$7440` | — | `core/gamedata_snapshot.py`:71<br>`render/play.py`:756, 762<br>`screens/colours.py`:7<br>`screens/panels.py`:98 |
| `$7453` | `sub_7453` | `render/pygame_app.py`:893 |
| `$7474` | — | `core/menu.py`:904 |
| `$74AD` | — | `core/menu.py`:904 |
| `$7569` | — | `core/ductmap.py`:7<br>`core/gamedata_snapshot.py`:54<br>`core/menu.py`:858, 860, 869<br>`core/nostromo.py`:19, 24, 71, 89, 181, 185…<br>`render/play.py`:530, 566, 969 |
| `$758B` | — | `core/map.py`:131<br>`core/nostromo.py`:19, 88 |
| `$758D` | — | `core/menu.py`:863<br>`render/play.py`:270, 274, 435, 1198 |
| `$75B1` | — | `core/menu.py`:863<br>`render/play.py`:270, 275, 435, 1198 |
| `$7640` | — | `core/menu.py`:901 |
| `$7653` | — | `core/menu.py`:901 |
| `$766F` | — | `core/menu.py`:148, 939 |
| `$7676` | — | `core/menu.py`:155 |
| `$7697` | — | `core/menu.py`:939 |
| `$76A4` | — | `core/menu.py`:157, 166 |
| `$76B4` | — | `core/menu.py`:158, 166 |
| `$76BB` | — | `core/nostromo.py`:185 |
| `$76D7` | — | `render/play.py`:271, 1199 |
| `$7720` | `guard_alien_present` | `core/menu.py`:116, 121, 378, 828, 843, 954…<br>`render/pygame_app.py`:201 |
| `$7732` | — | `render/pygame_app.py`:287 |
| `$773B` | — | `core/menu.py`:397 |
| `$7740` | — | `core/menu.py`:399<br>`core/state.py`:117 |
| `$7745` | — | `core/menu.py`:401 |
| `$774F` | — | `core/menu.py`:830 |
| `$7757` | — | `core/menu.py`:403, 405<br>`core/sim/__init__.py`:358<br>`core/sim/specials.py`:99 |
| `$7768` | — | `core/menu.py`:405<br>`core/sim/specials.py`:99 |
| `$778E` | — | `render/play.py`:273 |
| `$7797` | — | `core/menu.py`:499 |
| `$779C` | — | `core/menu.py`:23, 243<br>`core/nostromo.py`:36, 256<br>`core/sim/orders.py`:141, 586<br>`render/play.py`:1160 |
| `$77A7` | — | `core/menu.py`:247 |
| `$7860` | — | `core/alien.py`:175<br>`core/constants.py`:965<br>`core/gamedata_snapshot.py`:35<br>`core/menu.py`:247, 260, 265<br>`core/nostromo.py`:37, 255, 257<br>`core/sim/orders.py`:143 |
| `$7883` | — | `core/alien.py`:207<br>`core/menu.py`:266 |
| `$7888` | — | `core/alien.py`:205<br>`core/menu.py`:267 |
| `$7908` | — | `core/alien.py`:181, 205<br>`core/menu.py`:267 |
| `$7914` | — | `core/menu.py`:262 |
| `$7917` | — | `core/menu.py`:261 |
| `$7934` | — | `core/alien.py`:181, 218<br>`core/menu.py`:326 |
| `$7935` | `tbl_char_location` | `core/alien.py`:384, 652, 700, 823<br>`core/command_monitor.py`:135<br>`core/constants.py`:148, 173, 804, 817, 855, 971…<br>`core/crew.py`:304, 314, 328<br>`core/menu.py`:44, 361, 859<br>`core/nostromo.py`:226<br>`core/scoring.py`:45<br>`core/sim/__init__.py`:92, 189, 337, 340, 504, 514…<br>`core/sim/orders.py`:186<br>`core/sim/specials.py`:200, 282, 400<br>`render/endscreen.py`:192<br>`render/play.py`:236, 273, 331, 525 |
| `$7936` | — | `core/sim/__init__.py`:247 |
| `$793C` | — | `core/crew.py`:314<br>`core/sim/__init__.py`:92, 189 |
| `$793D` | — | `core/crew.py`:299, 304, 308, 341<br>`core/sim/__init__.py`:199 |
| `$7946` | — | `core/crew.py`:67 |
| `$7947` | — | `core/alien.py`:180, 190, 220<br>`core/menu.py`:266<br>`render/play.py`:331 |
| `$7948` | `set_room_screen_ptr` | `core/nostromo.py`:81 |
| `$7993` | `paint_map_colors` | `render/deck_backdrop.py`:32<br>`render/play.py`:865<br>`screens/colours.py`:8<br>`screens/panels.py`:145 |
| `$79B7` | — | `render/play.py`:866<br>`screens/panels.py`:161 |
| `$79CD` | `draw_control_panel_body` | `render/play.py`:302, 363 |
| `$7A10` | — | `core/constants.py`:70<br>`core/gamedata_snapshot.py`:66<br>`render/play.py`:287, 364, 366<br>`render/pygame_app.py`:263 |
| `$7A1C` | — | `render/play.py`:367 |
| `$7A3A` | `tbl_alien_route0` | `core/alien.py`:8, 120, 157<br>`core/gamedata_snapshot.py`:31 |
| `$7A5E` | — | `core/alien.py`:8, 121, 157 |
| `$7A82` | — | `core/alien.py`:8, 99, 101, 122, 157<br>`core/constants.py`:92 |
| `$7AA5` | — | `core/alien.py`:8, 99, 100, 101, 123, 157<br>`core/constants.py`:92 |
| `$7AC8` | — | `core/alien.py`:8, 99, 100, 101, 124, 157<br>`core/constants.py`:92 |
| `$7B02` | — | `core/sim/orders.py`:86, 89, 101 |
| `$7B4E` | — | `core/menu.py`:262 |
| `$7B69` | — | `core/constants.py`:999<br>`core/crew.py`:172<br>`core/sim/__init__.py`:153<br>`core/sim/orders.py`:86, 93, 107, 161, 169, 646 |
| `$7B6E` | — | `core/constants.py`:988<br>`core/sim/orders.py`:109, 275, 548 |
| `$7C3D` | `update_item_sprite` | `core/menu.py`:855<br>`core/nostromo.py`:93<br>`render/play.py`:1201 |
| `$7C5D` | — | `core/menu.py`:861<br>`core/nostromo.py`:95 |
| `$7C7D` | `tbl_item_names` | `core/items.py`:12 |
| `$7CC3` | — | `core/sim/specials.py`:365 |
| `$7CE2` | — | `core/menu.py`:515 |
| `$7CEB` | — | `core/constants.py`:425<br>`core/crew.py`:269<br>`render/pygame_app.py`:258, 263 |
| `$7D13` | — | `core/constants.py`:104, 125<br>`core/crew.py`:70, 200, 203, 219 |
| `$7D45` | `tbl_char_health` | `core/alien.py`:281, 752, 796, 853<br>`core/command_monitor.py`:138<br>`core/constants.py`:95, 232, 254, 256, 262, 281…<br>`core/crew.py`:71, 109, 112, 220, 288, 305…<br>`core/menu.py`:123, 385, 957, 962<br>`core/scoring.py`:41<br>`core/sim/__init__.py`:93, 342, 512<br>`core/sim/specials.py`:90, 281, 285, 339<br>`render/endscreen.py`:191<br>`render/play.py`:238 |
| `$7D46` | — | `core/sim/__init__.py`:248 |
| `$7D4D` | — | `core/constants.py`:418, 433<br>`core/crew.py`:111, 112, 305, 365, 399 |
| `$7D55` | `tbl_crew_fear` | `core/alien.py`:798<br>`core/constants.py`:77, 111, 374, 392, 897, 975…<br>`core/crew.py`:64, 96, 190, 226, 237, 306…<br>`core/scoring.py`:12<br>`core/sim/__init__.py`:318, 331, 345, 347, 513, 520… |
| `$7D56` | — | `core/sim/__init__.py`:248 |
| `$7D5D` | — | `core/crew.py`:95, 96, 103, 306, 372, 400 |
| `$7D94` | `health_band` | `core/constants.py`:424<br>`core/crew.py`:256 |
| `$7D9B` | — | `core/constants.py`:436<br>`core/crew.py`:258 |
| `$7DC5` | `fear_band` | `core/constants.py`:103, 424<br>`core/crew.py`:60, 200, 201<br>`core/sim/__init__.py`:359 |
| `$7DCB` | — | `core/crew.py`:224<br>`core/sim/__init__.py`:315<br>`render/play.py`:890 |
| `$7DCE` | — | `core/crew.py`:217 |
| `$7DD7` | — | `core/crew.py`:65 |
| `$7DDA` | — | `core/crew.py`:217 |
| `$7E5A` | — | `core/sim/__init__.py`:935 |
| `$7E68` | — | `render/play.py`:328 |
| `$7E69` | — | `render/play.py`:331 |
| `$7E71` | — | `render/play.py`:332 |
| `$7E76` | — | `render/play.py`:333 |
| `$7E79` | — | `render/play.py`:328 |
| `$7E82` | — | `render/play.py`:312 |
| `$7ED2` | — | `render/play.py`:333 |
| `$7EDB` | — | `render/play.py`:312, 395 |
| `$7EE5` | `clear_map_colors` | `core/ductmap.py`:18, 74<br>`render/play.py`:558 |
| `$7F0D` | `render_message` | `core/ductmap.py`:7<br>`core/gamedata_snapshot.py`:53<br>`render/play.py`:1126 |
| `$7F78` | `mark_exits` | `core/ductmap.py`:19, 72<br>`render/play.py`:1127 |
| `$7F7D` | — | `core/ductmap.py`:31 |
| `$7F85` | — | `core/ductmap.py`:33 |
| `$7F8F` | — | `core/ductmap.py`:55 |
| `$7FBC` | — | `core/ductmap.py`:55 |
| `$7FC0` | `set_color_at_ptr` | `core/ductmap.py`:34 |
| `$7FC8` | — | `core/ductmap.py`:35 |
| `$7FC9` | — | `core/ductmap.py`:35 |
| `$7FFE` | `color_if_char` | `core/ductmap.py`:76, 98, 108, 121 |
| `$8005` | — | `core/ductmap.py`:41 |
| `$8007` | — | `core/ductmap.py`:41, 124 |
| `$8009` | — | `core/ductmap.py`:121 |
| `$800A` | — | `core/ductmap.py`:98, 128 |
| `$800C` | — | `core/ductmap.py`:102, 130 |
| `$8027` | — | `core/ductmap.py`:109 |
| `$802C` | — | `core/ductmap.py`:102, 130 |
| `$804C` | — | `core/ductmap.py`:103, 131 |
| `$806D` | — | `core/ductmap.py`:110 |
| `$807F` | — | `core/alien.py`:221<br>`core/menu.py`:287 |
| `$8080` | — | `core/map.py`:181<br>`core/menu.py`:286, 311 |
| `$8089` | — | `core/alien.py`:222<br>`core/menu.py`:287 |
| `$8093` | — | `core/alien.py`:221<br>`core/menu.py`:287 |
| `$809D` | — | `core/alien.py`:222<br>`core/menu.py`:287 |
| `$80B1` | — | `core/ductmap.py`:12<br>`core/nostromo.py`:189 |
| `$80D3` | `tbl_room_deck` | `core/ductmap.py`:12<br>`core/nostromo.py`:25, 72, 181, 182, 184, 189… |
| `$80F5` | `tbl_alien_duct0` | `core/constants.py`:142, 166, 956<br>`core/gamedata_snapshot.py`:40<br>`core/map.py`:175 |
| `$8117` | `tbl_room_south` | `core/constants.py`:142, 167, 956, 966<br>`core/gamedata_snapshot.py`:40<br>`core/map.py`:175 |
| `$8139` | `tbl_room_east` | `core/constants.py`:143, 168, 956, 966<br>`core/gamedata_snapshot.py`:40<br>`core/map.py`:175 |
| `$815B` | `tbl_room_west` | `core/constants.py`:143, 169, 956<br>`core/gamedata_snapshot.py`:40<br>`core/map.py`:175 |
| `$817D` | `select_menu_template` | `core/ductmap.py`:5<br>`core/gamedata_snapshot.py`:53<br>`render/play.py`:1125 |
| `$81C9` | — | `core/nostromo.py`:183 |
| `$81D7` | — | `core/menu.py`:249 |
| `$81EF` | — | `core/alien.py`:215<br>`core/map.py`:182<br>`core/menu.py`:249, 260, 269, 286, 307, 309<br>`core/nostromo.py`:38, 258<br>`core/sim/orders.py`:144, 586, 618 |
| `$81F2` | — | `core/alien.py`:218, 229<br>`core/menu.py`:270, 326 |
| `$8271` | — | `core/map.py`:182 |
| `$829A` | — | `core/crew.py`:82, 131, 134<br>`core/menu.py`:423<br>`core/sim/orders.py`:241<br>`core/sim/specials.py`:469 |
| `$829B` | — | `core/crew.py`:82, 131, 135<br>`core/sim/orders.py`:241, 252 |
| `$82B5` | — | `core/menu.py`:481 |
| `$82CF` | `tbl_item_type` | `core/items.py`:12 |
| `$82E3` | `tbl_room_objects` | `core/items.py`:12<br>`core/sim/__init__.py`:224<br>`core/sim/specials.py`:278, 279, 398 |
| `$8332` | — | `core/crew.py`:82, 132 |
| `$836F` | — | `screens/panels.py`:120 |
| `$8387` | `draw_item_row2` | `screens/panels.py`:118 |
| `$83AF` | — | `core/crew.py`:133 |
| `$83C6` | — | `core/crew.py`:133 |
| `$83DA` | — | `screens/panels.py`:122 |
| `$83E0` | — | `screens/panels.py`:119 |
| `$83FD` | — | `core/menu.py`:995 |
| `$8437` | `route_command` | `core/menu.py`:488, 492<br>`core/orders.py`:54<br>`core/sim/orders.py`:317 |
| `$845A` | — | `core/constants.py`:1017<br>`core/sim/orders.py`:222, 647 |
| `$8460` | — | `core/constants.py`:989<br>`core/menu.py`:993<br>`core/sim/orders.py`:248, 265, 549 |
| `$8465` | — | `core/sim/orders.py`:222 |
| `$8512` | — | `core/sim/orders.py`:252 |
| `$8527` | — | `core/sim/orders.py`:252 |
| `$8530` | — | `core/sim/orders.py`:532 |
| `$8573` | — | `core/menu.py`:497 |
| `$858D` | — | `core/menu.py`:498 |
| `$85B1` | — | `core/sim/orders.py`:532 |
| `$8660` | `wait_keypress_flash` | `render/pygame_app.py`:516, 546, 1050 |
| `$8666` | — | `render/pygame_app.py`:99 |
| `$8676` | `tbl_grille_access` | `core/alien.py`:434, 444, 451<br>`core/constants.py`:185, 196<br>`core/map.py`:66<br>`core/menu.py`:298<br>`core/nostromo.py`:270<br>`core/orders.py`:39 |
| `$86BE` | — | `core/menu.py`:348 |
| `$86C8` | — | `core/orders.py`:42<br>`render/play.py`:849, 1089 |
| `$86D7` | — | `render/play.py`:1089 |
| `$86E6` | — | `core/menu.py`:526, 614<br>`core/orders.py`:41 |
| `$86F0` | `draw_grille_option` | `core/menu.py`:307, 526, 564, 568, 570<br>`core/orders.py`:38, 39, 44, 45<br>`core/sim/orders.py`:211, 611 |
| `$86F3` | — | `core/menu.py`:315 |
| `$86FA` | — | `core/sim/orders.py`:621 |
| `$8710` | — | `render/play.py`:592, 849 |
| `$8729` | — | `core/menu.py`:312<br>`core/sim/orders.py`:211, 602, 611 |
| `$8749` | `sub_char_special` | `core/sim/orders.py`:289 |
| `$8754` | — | `core/sim/__init__.py`:499 |
| `$8784` | — | `core/menu.py`:423, 493<br>`core/orders.py`:54, 57<br>`core/sim/orders.py`:202, 316 |
| `$8787` | — | `core/constants.py`:909<br>`core/sim/orders.py`:204, 309<br>`core/sim/specials.py`:463 |
| `$878C` | — | `core/sim/specials.py`:489 |
| `$879A` | — | `core/constants.py`:920<br>`core/sim/orders.py`:310<br>`core/sim/specials.py`:500 |
| `$87A1` | — | `core/constants.py`:912, 919<br>`core/sim/specials.py`:513 |
| `$87AA` | — | `core/constants.py`:912, 919<br>`core/sim/specials.py`:513 |
| `$87B0` | — | `core/sim/specials.py`:515 |
| `$87B6` | — | `core/sim/specials.py`:518<br>`core/state.py`:97 |
| `$87C9` | — | `core/constants.py`:921<br>`core/sim/orders.py`:310<br>`core/sim/specials.py`:469, 500 |
| `$87D7` | — | `core/sim/specials.py`:518<br>`core/state.py`:97 |
| `$87EE` | — | `core/sim/specials.py`:517 |
| `$880E` | — | `core/constants.py`:909<br>`core/sim/specials.py`:463 |
| `$883C` | — | `core/constants.py`:910<br>`core/sim/specials.py`:468, 479 |
| `$8844` | — | `render/play.py`:239<br>`screens/panels.py`:200 |
| `$884A` | — | `render/play.py`:233<br>`screens/panels.py`:191 |
| `$8860` | — | `core/menu.py`:488, 489<br>`render/play.py`:233 |
| `$887E` | `tbl_rng_scramble` | `core/constants.py`:913, 918 |
| `$888F` | `rng` | `core/alien.py`:5<br>`core/constants.py`:132 |
| `$88AB` | `sub_88ab_prechar` | `core/constants.py`:654<br>`core/sim/__init__.py`:795 |
| `$88B6` | — | `core/constants.py`:36, 655, 923<br>`core/sim/__init__.py`:148, 822 |
| `$88BB` | — | `core/sim/__init__.py`:836 |
| `$88C1` | — | `core/sim/__init__.py`:836 |
| `$88C3` | — | `core/sim/__init__.py`:839 |
| `$88C9` | — | `core/sim/__init__.py`:840 |
| `$88CC` | `guard_6580` | `core/menu.py`:489<br>`render/play.py`:197, 223<br>`screens/panels.py`:189 |
| `$88D2` | — | `render/play.py`:225<br>`screens/panels.py`:196 |
| `$88E8` | — | `core/menu.py`:492 |
| `$88F4` | — | `core/menu.py`:410 |
| `$88F9` | — | `render/play.py`:204<br>`render/pygame_app.py`:296<br>`screens/panels.py`:193 |
| `$8901` | — | `render/play.py`:205 |
| `$8903` | — | `render/play.py`:206 |
| `$8907` | — | `render/play.py`:208 |
| `$890A` | — | `screens/panels.py`:193 |
| `$890C` | — | `render/play.py`:248, 827, 911<br>`screens/panels.py`:189 |
| `$8917` | — | `screens/panels.py`:189 |
| `$8919` | — | `render/play.py`:199<br>`render/pygame_app.py`:296 |
| `$891E` | — | `core/menu.py`:496 |
| `$8924` | — | `core/menu.py`:496 |
| `$8927` | — | `core/menu.py`:410 |
| `$8932` | — | `render/play.py`:205, 206, 208, 229, 230, 231…<br>`screens/panels.py`:201 |
| `$8934` | — | `render/play.py`:250 |
| `$8944` | — | `render/play.py`:252 |
| `$8949` | — | `render/play.py`:254 |
| `$8951` | — | `screens/panels.py`:207 |
| `$8971` | — | `core/alien.py`:133<br>`core/constants.py`:656<br>`core/sim/__init__.py`:795, 806, 811, 823, 840 |
| `$8974` | — | `core/alien.py`:116, 129 |
| `$89A6` | — | `core/alien.py`:116 |
| `$89AC` | — | `core/constants.py`:293 |
| `$89AF` | — | `core/alien.py`:274, 662 |
| `$89B1` | — | `core/alien.py`:269, 655 |
| `$89BF` | — | `core/alien.py`:527<br>`core/constants.py`:195 |
| `$89C2` | — | `core/alien.py`:527 |
| `$89C4` | — | `core/alien.py`:495, 511, 512, 514, 515, 516…<br>`core/constants.py`:201 |
| `$89C7` | — | `core/constants.py`:210 |
| `$89CE` | — | `core/alien.py`:275, 514 |
| `$89D0` | — | `core/alien.py`:499, 551 |
| `$89D5` | — | `core/alien.py`:515, 551 |
| `$89D7` | `alien_enter_duct` | `core/alien.py`:553 |
| `$89E0` | — | `core/constants.py`:156 |
| `$89E8` | — | `core/alien.py`:65<br>`core/constants.py`:212 |
| `$89F2` | — | `core/alien.py`:586, 595 |
| `$89F7` | — | `core/alien.py`:540, 568 |
| `$89FA` | — | `core/alien.py`:585 |
| `$89FF` | — | `core/alien.py`:517 |
| `$8A04` | — | `core/alien.py`:516, 568, 583 |
| `$8A07` | — | `core/alien.py`:571 |
| `$8A09` | — | `core/alien.py`:273, 591, 614, 664 |
| `$8A0C` | — | `core/alien.py`:593 |
| `$8A11` | — | `core/alien.py`:570, 585 |
| `$8A12` | — | `core/constants.py`:212 |
| `$8A1C` | — | `core/constants.py`:212 |
| `$8A26` | — | `core/constants.py`:212 |
| `$8A36` | `alien_choose_move` | `core/alien.py`:5, 14, 545<br>`core/constants.py`:131, 158, 199 |
| `$8A39` | — | `core/constants.py`:209 |
| `$8A40` | — | `core/alien.py`:64<br>`core/constants.py`:211 |
| `$8A47` | — | `core/alien.py`:14 |
| `$8A4A` | — | `core/constants.py`:147 |
| `$8A50` | — | `core/constants.py`:211 |
| `$8A5A` | — | `core/constants.py`:211 |
| `$8A64` | — | `core/constants.py`:211 |
| `$8A74` | `alien_ai` | `core/alien.py`:16, 459<br>`core/constants.py`:141, 162, 163 |
| `$8A7A` | — | `core/alien.py`:464<br>`core/constants.py`:178 |
| `$8A7C` | — | `core/alien.py`:472<br>`core/constants.py`:179 |
| `$8A83` | — | `core/alien.py`:464, 472<br>`core/constants.py`:179 |
| `$8A8B` | — | `core/constants.py`:177 |
| `$8A90` | — | `core/alien.py`:275 |
| `$8A92` | — | `core/alien.py`:462, 670<br>`core/constants.py`:173 |
| `$8A9E` | — | `core/constants.py`:176 |
| `$8AA2` | — | `core/map.py`:183 |
| `$8AAB` | — | `core/alien.py`:489<br>`core/constants.py`:214 |
| `$8AB4` | — | `core/constants.py`:176 |
| `$8ABE` | — | `core/constants.py`:176 |
| `$8ACB` | — | `core/map.py`:183 |
| `$8ACE` | `alien_tick` | `core/alien.py`:637 |
| `$8AD4` | — | `core/alien.py`:639 |
| `$8AD7` | — | `core/alien.py`:770 |
| `$8AE1` | — | `core/alien.py`:32, 676<br>`core/constants.py`:439 |
| `$8AE4` | — | `core/alien.py`:33, 270, 679, 680, 684, 699<br>`core/constants.py`:458 |
| `$8B03` | — | `core/alien.py`:652 |
| `$8B13` | — | `core/alien.py`:270, 652, 699, 729 |
| `$8B6F` | — | `core/alien.py`:463<br>`core/constants.py`:175 |
| `$8B7E` | — | `core/constants.py`:175 |
| `$8B7F` | — | `core/alien.py`:443<br>`core/constants.py`:184 |
| `$8B84` | — | `core/alien.py`:265, 440<br>`core/constants.py`:183 |
| `$8B86` | — | `core/alien.py`:451 |
| `$8B8C` | — | `core/constants.py`:186, 189 |
| `$8B94` | — | `core/alien.py`:452 |
| `$8B95` | — | `core/alien.py`:478 |
| `$8BB1` | — | `core/alien.py`:553 |
| `$8BB4` | — | `core/alien.py`:444<br>`core/constants.py`:185 |
| `$8BC4` | — | `core/constants.py`:188<br>`render/play.py`:594, 913, 997<br>`screens/panels.py`:211, 214 |
| `$8C49` | `find_crew_with_alien` | `core/command_monitor.py`:132<br>`core/menu.py`:591, 634<br>`screens/panels.py`:212 |
| `$8C4B` | — | `core/command_monitor.py`:135 |
| `$8C4E` | — | `core/command_monitor.py`:157 |
| `$8C53` | — | `core/command_monitor.py`:136 |
| `$8C56` | — | `core/command_monitor.py`:159<br>`core/menu.py`:597 |
| `$8C5B` | — | `core/command_monitor.py`:125, 138<br>`core/menu.py`:600 |
| `$8C5E` | — | `core/command_monitor.py`:161 |
| `$8C60` | — | `core/command_monitor.py`:161 |
| `$8C76` | — | `core/menu.py`:586, 589, 624, 642 |
| `$8C80` | `reset_attack_state` | `core/alien.py`:279, 696, 705<br>`core/sim/__init__.py`:934, 953<br>`core/sim/orders.py`:406<br>`render/audio.py`:236, 245<br>`render/play.py`:1100 |
| `$8C82` | — | `audio/sfx.py`:164<br>`core/sound.py`:33 |
| `$8C85` | — | `core/sim/__init__.py`:476, 479, 532 |
| `$8C8D` | — | `audio/sfx.py`:94 |
| `$8C8F` | — | `core/sim/__init__.py`:973 |
| `$8C98` | — | `audio/sfx.py`:104 |
| `$8CCC` | — | `render/play.py`:1003<br>`screens/panels.py`:218 |
| `$8CD6` | — | `screens/panels.py`:218 |
| `$8CD9` | — | `core/alien.py`:278, 695, 800<br>`core/menu.py`:570, 582, 590, 626, 642<br>`core/sim/__init__.py`:476, 478, 529, 538 |
| `$8CDC` | — | `core/alien.py`:771 |
| `$8CE1` | — | `core/alien.py`:802<br>`core/command_monitor.py`:145<br>`core/menu.py`:564, 568, 570, 592, 623, 643<br>`core/sound.py`:12, 47, 59<br>`render/audio.py`:10, 194, 234<br>`render/play.py`:546, 1000, 1098<br>`render/pygame_app.py`:448, 450<br>`screens/panels.py`:213, 221 |
| `$8CEB` | — | `core/menu.py`:623 |
| `$8CF3` | — | `core/alien.py`:800<br>`core/sim/__init__.py`:538 |
| `$8D10` | — | `render/play.py`:997<br>`screens/panels.py`:211 |
| `$8D1A` | `begin_active_seq` | `render/play.py`:557 |
| `$8D26` | — | `core/sound.py`:12 |
| `$8D71` | `resolve_char_display_loc` | `core/sim/orders.py`:337 |
| `$8DB6` | — | `core/alien.py`:153<br>`core/constants.py`:645 |
| `$8DD1` | — | `core/alien.py`:153 |
| `$8DDC` | — | `core/sim/orders.py`:355 |
| `$8DF0` | — | `core/sim/__init__.py`:534<br>`core/sound.py`:74<br>`render/audio.py`:126 |
| `$8DF6` | — | `audio/sfx.py`:163<br>`core/sound.py`:32, 74 |
| `$8E32` | `check_6562` | `core/sim/__init__.py`:485, 954<br>`core/sim/orders.py`:407 |
| `$8E39` | — | `core/sim/__init__.py`:486 |
| `$8EBD` | `guard_6562` | `core/alien.py`:657, 661, 727<br>`core/constants.py`:290, 294<br>`core/sim/__init__.py`:535 |
| `$8EC3` | — | `core/constants.py`:295 |
| `$8EC8` | — | `core/constants.py`:296 |
| `$8ED0` | — | `core/constants.py`:290, 307 |
| `$8F0B` | — | `core/sim/orders.py`:338, 355, 374 |
| `$8F1B` | — | `core/sim/orders.py`:338, 382 |
| `$8F2D` | — | `core/sim/orders.py`:345 |
| `$8F31` | — | `core/sim/orders.py`:397 |
| `$8F3B` | — | `core/sim/orders.py`:345 |
| `$8F3E` | — | `core/sim/orders.py`:349, 400 |
| `$8F50` | — | `core/sim/orders.py`:349 |
| `$8FFC` | `init_b_music` | `audio/intro.py`:14, 31 |
| `$9013` | — | `audio/sfx.py`:86 |
| `$9039` | `title_music_player` | `audio/intro.py`:15<br>`audio/sid.py`:89 |
| `$91A1` | — | `audio/intro.py`:16 |
| `$91AE` | — | `audio/intro.py`:18 |
| `$91BA` | — | `audio/intro.py`:18 |
| `$91C6` | — | `audio/intro.py`:17 |
| `$91CE` | — | `audio/intro.py`:17 |
| `$91D6` | — | `audio/intro.py`:72 |
| `$9528` | `setup_cursor_sprite` | `render/pygame_app.py`:179 |
| `$954C` | — | `render/pygame_app.py`:179 |
| `$95B7` | — | `core/sim/specials.py`:424<br>`core/state.py`:223 |
| `$9600` | — | `audio/sfx.py`:112 |
| `$A000` | — | `assets.py`:125<br>`core/gamedata_snapshot.py`:60<br>`render/play.py`:491, 532 |
| `$A21C` | — | `core/gamedata_snapshot.py`:60<br>`render/play.py`:491, 532 |
| `$A438` | — | `core/gamedata_snapshot.py`:60<br>`render/play.py`:491, 532 |
| `$A65E` | — | `core/constants.py`:1021<br>`core/opening_name.py`:10, 13, 14<br>`render/frontend.py`:1224<br>`render/play.py`:239, 1002<br>`screens/panels.py`:202, 215 |
| `$A690` | — | `core/opening_name.py`:20 |
| `$A712` | — | `core/menu.py`:152, 168 |
| `$A715` | — | `core/menu.py`:220, 518 |
| `$A71C` | `tbl_room_names` | `core/nostromo.py`:82 |
| `$A7C6` | — | `core/menu.py`:168 |
| `$A7D0` | — | `core/menu.py`:154, 169 |
| `$A86E` | — | `core/orders.py`:31 |
| `$A898` | — | `core/menu.py`:439 |
| `$A8DF` | — | `core/menu.py`:447 |
| `$A956` | — | `core/ductmap.py`:6<br>`core/gamedata_snapshot.py`:53 |
| `$A9C4` | — | `core/ductmap.py`:6<br>`core/gamedata_snapshot.py`:53 |
| `$AA6E` | — | `core/ductmap.py`:6<br>`core/gamedata_snapshot.py`:53 |
| `$BFFF` | — | `assets.py`:125 |
| `$D000` | — | `assets.py`:128<br>`render/frontend.py`:104, 150, 241, 934<br>`render/pygame_app.py`:184 |
| `$D001` | — | `render/frontend.py`:104, 150, 934<br>`render/pygame_app.py`:184 |
| `$D002` | — | `core/menu.py`:862, 863<br>`core/nostromo.py`:95<br>`render/frontend.py`:150<br>`render/play.py`:274 |
| `$D003` | — | `core/menu.py`:863<br>`render/frontend.py`:150<br>`render/play.py`:275 |
| `$D004` | — | `render/play.py`:965 |
| `$D005` | — | `render/play.py`:962 |
| `$D006` | — | `render/pygame_app.py`:285 |
| `$D007` | — | `render/pygame_app.py`:289 |
| `$D008` | — | `render/play.py`:142 |
| `$D00A` | — | `render/play.py`:143 |
| `$D00C` | — | `render/play.py`:142 |
| `$D00D` | — | `render/play.py`:143 |
| `$D00E` | — | `render/play.py`:143 |
| `$D00F` | — | `render/play.py`:143 |
| `$D010` | — | `render/frontend.py`:104, 242, 934<br>`render/play.py`:144 |
| `$D015` | — | `render/pygame_app.py`:312, 318 |
| `$D017` | — | `render/play.py`:141, 156 |
| `$D018` | — | `render/pygame_app.py`:253, 707<br>`render/romfont.py`:7 |
| `$D019` | — | `audio/intro.py`:7, 9, 12, 32, 141<br>`audio/mos6502.py`:42<br>`render/pygame_app.py`:336 |
| `$D01B` | — | `render/pygame_app.py`:185, 1162, 1210 |
| `$D01C` | — | `render/pygame_app.py`:186, 314, 1162 |
| `$D01D` | — | `render/play.py`:141, 156 |
| `$D020` | — | `core/constants.py`:591<br>`core/state.py`:176<br>`render/endscreen.py`:153<br>`render/frontend.py`:1212<br>`render/play.py`:623, 625<br>`render/pygame_app.py`:93, 518, 519<br>`screens/colours.py`:29 |
| `$D021` | — | `core/constants.py`:870<br>`core/sim/__init__.py`:443, 467, 470<br>`core/state.py`:113, 185, 187, 188, 193, 203<br>`render/frontend.py`:206, 564, 1172, 1175, 1231<br>`render/play.py`:604, 811, 902<br>`render/pygame_app.py`:1209, 1217<br>`render/text.py`:98, 109 |
| `$D025` | — | `render/frontend.py`:127, 136 |
| `$D026` | — | `render/frontend.py`:128, 137 |
| `$D027` | — | `render/frontend.py`:102, 935, 1179<br>`render/layout.py`:45<br>`render/play.py`:13, 105, 1236<br>`render/pygame_app.py`:184, 321 |
| `$D028` | — | `render/play.py`:1196 |
| `$D029` | — | `render/play.py`:263, 964 |
| `$D02A` | — | `render/play.py`:187 |
| `$D02B` | — | `render/play.py`:144, 155<br>`render/pygame_app.py`:317 |
| `$D02C` | — | `render/pygame_app.py`:317 |
| `$D02D` | — | `render/pygame_app.py`:317 |
| `$D02E` | — | `render/frontend.py`:1179<br>`render/play.py`:144, 155<br>`render/pygame_app.py`:317, 321 |
| `$D400` | — | `audio/__init__.py`:10<br>`audio/intro.py`:36<br>`audio/mos6502.py`:44<br>`audio/sid.py`:3 |
| `$D401` | — | `audio/sfx.py`:78, 187, 267 |
| `$D404` | — | `audio/sfx.py`:76, 192, 308, 309 |
| `$D405` | — | `audio/sfx.py`:81, 188 |
| `$D406` | — | `audio/sfx.py`:82, 184, 189 |
| `$D408` | — | `audio/sfx.py`:268 |
| `$D40B` | — | `audio/sfx.py`:77 |
| `$D40D` | — | `audio/sfx.py`:23, 83 |
| `$D40F` | — | `audio/sfx.py`:80, 160 |
| `$D413` | — | `audio/intro.py`:71<br>`audio/sfx.py`:79, 161<br>`audio/sid.py`:104, 105 |
| `$D415` | — | `audio/sid.py`:288 |
| `$D416` | — | `audio/intro.py`:16<br>`audio/sid.py`:93, 100, 108, 288, 304 |
| `$D417` | — | `audio/intro.py`:21<br>`audio/sid.py`:24, 286 |
| `$D418` | — | `audio/__init__.py`:10<br>`audio/intro.py`:21, 36<br>`audio/mos6502.py`:44<br>`audio/sid.py`:25, 287 |
| `$D41B` | — | `audio/sfx.py`:267<br>`audio/sid.py`:318 |
| `$D41C` | — | `audio/intro.py`:16, 35<br>`audio/mos6502.py`:42<br>`audio/sid.py`:27, 93, 99, 313 |
| `$D800` | — | `render/deck_backdrop.py`:24<br>`render/frontend.py`:751<br>`render/pygame_app.py`:133, 203<br>`render/text.py`:14<br>`screens/colours.py`:28<br>`screens/panels.py`:46 |
| `$D81E` | — | `screens/panels.py`:53 |
| `$D9EB` | — | `render/endscreen.py`:58 |
| `$DAD0` | — | `screens/panels.py`:148 |
| `$DAF8` | — | `screens/panels.py`:149 |
| `$DB20` | — | `screens/panels.py`:149 |
| `$DB48` | — | `screens/panels.py`:150 |
| `$DB70` | — | `screens/panels.py`:150 |
| `$DB98` | — | `screens/panels.py`:151 |
| `$DBC0` | — | `screens/panels.py`:151 |
| `$DBE7` | — | `render/deck_backdrop.py`:24 |
| `$DC00` | — | `render/pygame_app.py`:502, 894, 955 |
| `$DFFF` | — | `assets.py`:128 |
| `$E000` | — | `audio/intro.py`:39 |
| `$EA31` | — | `audio/intro.py`:28 |
| `$EA7E` | — | `audio/intro.py`:11 |

## By module

How much of each module is anchored to the ROM.

| module | distinct addresses |
|---|---|
| `core/constants.py` | 300 |
| `render/play.py` | 177 |
| `core/sim/__init__.py` | 166 |
| `core/menu.py` | 142 |
| `core/alien.py` | 140 |
| `core/sim/specials.py` | 104 |
| `core/sim/orders.py` | 89 |
| `render/frontend.py` | 82 |
| `render/pygame_app.py` | 70 |
| `audio/sfx.py` | 62 |
| `core/state.py` | 58 |
| `render/endscreen.py` | 52 |
| `core/crew.py` | 50 |
| `screens/panels.py` | 47 |
| `core/scoring.py` | 43 |
| `screens/ending.py` | 35 |
| `audio/intro.py` | 30 |
| `core/ductmap.py` | 28 |
| `core/gamedata_snapshot.py` | 25 |
| `core/nostromo.py` | 20 |
| `core/flow.py` | 19 |
| `render/audio.py` | 18 |
| `core/orders.py` | 15 |
| `core/sound.py` | 14 |
| `core/map.py` | 13 |
| `core/command_monitor.py` | 13 |
| `render/layout.py` | 12 |
| `core/special_options.py` | 12 |
| `audio/sid.py` | 11 |
| `render/deck_backdrop.py` | 10 |
| `core/modes.py` | 8 |
| `core/opening_name.py` | 8 |
| `core/items.py` | 7 |
| `screens/colours.py` | 5 |
| `assets.py` | 4 |
| `audio/mos6502.py` | 4 |
| `render/tiles.py` | 4 |
| `render/romfont.py` | 3 |
| `core/sim/protocol.py` | 3 |
| `render/text.py` | 3 |
| `audio/__init__.py` | 2 |
| `app.py` | 1 |
