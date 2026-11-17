| Case          | Depth | Expected    | Chosen      | Met |  Nodes | Search ms |
| ------------- | ----: | ----------- | ----------- | --- | -----: | --------: |
| forced_switch |     1 | switch:3    | switch:3    | yes |    210 |       2.6 |
| forced_switch |     2 | switch:3    | switch:3    | yes |   4865 |      55.9 |
| forced_switch |     3 | switch:3    | switch:3    | yes | 100455 |    1223.2 |
| ko_available  |     1 | liquidation | liquidation | yes |     48 |       0.7 |
| ko_available  |     2 | liquidation | liquidation | yes |   1523 |      17.4 |
| ko_available  |     3 | liquidation | liquidation | yes |  43257 |     477.2 |
| setup_move    |     1 | bulkup      | drainpunch  | no  |     64 |       0.8 |
| setup_move    |     2 | bulkup      | drainpunch  | no  |   4395 |      44.9 |
| setup_move    |     3 | bulkup      | bulkup      | yes | 294723 |    2818.7 |
