# STATUS: HASH-ANCHORED, RAW WITHHELD — the evidence bank and row-level transcripts

*(Labeling per CDX #013 F2: a hash commits IDENTITY, not availability, and never
chronology. Claims backed by these files carry this status explicitly and are never
presented as openly checkable.)*

The entropy-arm studies test whether models fabricate when citing evidence. To make the
test real, the 24-item bank embeds clause-grounded renderings of paid standards documents
(ISO/IEC 17025, ISO/IEC 17043, AIAG MSA-4, UKAS LAB-48, Eurachem PT, JCGM/VIM) — several
blocks track the source text closely enough that republishing them would reproduce
copyrighted standard prose. The row-level model transcripts quote those blocks back
(the scorer explicitly tags COPY rows), so they carry the same text.

**What is public:** the aggregate results (`v2_results.json`, `entropy_pilot_results.json`),
the run and scoring code (`entropy_v2_run.py`, `entropy_pilot.py`), and the design doc.
Every number cited publicly derives from the aggregate files.

**What is withheld and hash-anchored:** the bank items and raw rows below. Auditors who
hold licensed copies of the standards can request the withheld set for verification;
the hashes bind what they receive to what produced the published aggregates.

| file | bytes | sha256 |
|---|---|---|
| `benchmark/entropy_arm/bank/item_01.json` | 3158 | `6a8705a4093b6de151cdbe1a1e3e3d762f810cf26f4ac33e95d1c5ee5ccf279c` |
| `benchmark/entropy_arm/bank/item_02.json` | 3070 | `42acff5d00b03fb8daa7a7473ee1bb6332f125e7a30a140bda1eef5785b460ca` |
| `benchmark/entropy_arm/bank/item_03.json` | 3225 | `16de178d83fa0f23ba82c91e9f7cbfcb3f99a8ef584aadbc347d89b87cbc1fbe` |
| `benchmark/entropy_arm/bank/item_04.json` | 2667 | `3dce702099ebc5545146aad87d1726c026479129041824c5e5da026662fa0889` |
| `benchmark/entropy_arm/bank/item_05.json` | 1751 | `ffc44c724d994bc6f00a2b24b64663de0da0dbb05d2cfe4a271d8728c49d35db` |
| `benchmark/entropy_arm/bank/item_06.json` | 3269 | `34a617ec4e2fc3fffc747a1efec21400823c5991ad2b14f8e59858bb554bbdb0` |
| `benchmark/entropy_arm/bank/item_07.json` | 2765 | `1f829700f9979662a5bb3d013dad59c7810ab4939d4b1dd1ecb0d92ddd66eb7f` |
| `benchmark/entropy_arm/bank/item_08.json` | 1961 | `e69336cad91a5c5cb0bcf8ab0f738a4d928ed0d61c58e9a55b0931cff1863893` |
| `benchmark/entropy_arm/bank/item_09.json` | 3937 | `5301f1831a901717a82dc15e84efe84f67a75d199849a3fb8b5338326ec28490` |
| `benchmark/entropy_arm/bank/item_10.json` | 3300 | `3aa60a81cf80670a1f3927f4cc2cb04443a390939c7c59e0af67276d1670366f` |
| `benchmark/entropy_arm/bank/item_11.json` | 3330 | `ef90050a6596775dfa4e7138fcfc6ef7fa926e87e42b472be04dbc5953e10d2a` |
| `benchmark/entropy_arm/bank/item_12.json` | 3252 | `924978e1ea793c7866ff8352f05776bc3a51491fcd53e399d3847ba21644697b` |
| `benchmark/entropy_arm/bank/item_13.json` | 3197 | `737d5b51436be104dc0caf2575435bc41b50c633637780fd473a76a6bf19467c` |
| `benchmark/entropy_arm/bank/item_14.json` | 3243 | `e3d5cf11b81b72bc5dd8988609832446e17f05ed75b7cf2c7198f5e13f271e52` |
| `benchmark/entropy_arm/bank/item_15.json` | 2200 | `26a547b2835a3e13c457a312f4338f92b43ad4584c8e6f43bb500e317829ae6c` |
| `benchmark/entropy_arm/bank/item_16.json` | 3646 | `a04410dd3fae5ecdd076674e03581755e8f98744dad9e3ecd0e63ac1885dc944` |
| `benchmark/entropy_arm/bank/item_17.json` | 2928 | `fc2ce9ab3db5a009d55ada80d9b92726e808c603d3a1170b6093839fd8316cba` |
| `benchmark/entropy_arm/bank/item_18.json` | 3331 | `200f1bedca35c1c21b70bd1d9e23e53586c210bc358aa5e92ea23a6b1d5cf8ff` |
| `benchmark/entropy_arm/bank/item_19.json` | 2812 | `399ac6263e8dd340ff17ab7e87ac006ac5d10dea935ab1e90721242d0ac24ef5` |
| `benchmark/entropy_arm/bank/item_20.json` | 3709 | `53b6ac827f57ff93555b4933f30aa28f5ebc28a8a57b9d891d9bc46c9adefa88` |
| `benchmark/entropy_arm/bank/item_21.json` | 3704 | `0806ae9f3c987612e5f13a600c0ff6d252bdc837e34d39b248eba49301ac417a` |
| `benchmark/entropy_arm/bank/item_22.json` | 3267 | `259d9721e0bd5e21ca00aede858f356e4d4e7463dfe7dac4000f072868f0ec91` |
| `benchmark/entropy_arm/bank/item_23.json` | 3168 | `87ce72a46b67399afae5a2816da56e813a4a14bddd69ef58e753b0dcbc7732bb` |
| `benchmark/entropy_arm/bank/item_24.json` | 3237 | `c1eeba7ba43941a80b82a89972065b78d038c1c5a9f6086105b2cfedd24fdc0b` |
| `benchmark/entropy_arm/v2_rows.jsonl` | 304504 | `d7dea2bb18e453fecb0634617e7c5b0ca43be6518aa79fb6ae3276ca8dd7d3b3` |
| `benchmark/entropy_arm/v2_rows_rescored.jsonl` | 304479 | `c64aebdbe861ceb573bf5db5822ac603cfe9c0e0f74f22472122bd4d7797b6dc` |
| `benchmark/entropy_arm/entropy_pilot_rows.jsonl` | 57596 | `e20e1d78cc5370c66af9b24629a098fccf7bf4f7a9062c184e53c27eb3378d53` |
