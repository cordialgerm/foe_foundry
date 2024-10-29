---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:172300
- loss:TripletLoss
widget:
- source_sentence: agile creature that causes uncontrollable laughter
  sentences:
  - 'Here are some interesting facts about Silenal: Immune to charmed and poisoned
    conditions. Gains benefit from alcohol to enhance abilities. Can hide effectively
    in combat situations. Truesight ability enables it to see through illusions near
    alcohol. Provides advantages to allies in social settings. '
  - 'Lost Minotaur is described as: The Lost Minotaur is a large undead creature with
    a massive frame and a twisted appearance, wielding a large Twilight Greataxe.
    Lost Minotaur is known for: Its ability to sense living creatures from a mile
    away and the devastating charge attack make it a menacing presence. '
  - 'Shurale is known as: The Shurale is a medium-sized fey creature with a sly demeanor,
    characterized by high Dexterity and Charisma. It uses a combination of physical
    attacks and magical abilities to incapacitate foes. Shurale is remarkable for:
    Its unique Tickle ability can incapacitate enemies with laughter, making it a
    formidable opponent in combat. '
- source_sentence: dragon worshiping humanoid
  sentences:
  - 'Young Void Dragon is present in: Typically found in chaotic, alien planes or
    regions steeped in elemental conflict. Young Void Dragon has the following relations:
    Related to other dragon species and potentially allied with creatures of the Void.
    Young Void Dragon is driven by: To unleash chaos and inflict damage upon foes,
    while navigating both physical and void environments effortlessly. '
  - 'Arx is proficient in: High physical strength and significant damage resistances
    to elemental attacks. Arx is good at: Proficient in Athletics and has a decent
    Perception skill. Arx can use: Wall Smash which can deal substantial bludgeoning
    damage in a wide area and control enemy movement. Arx can use: The Arx unleashes
    powerful melee attacks with its claws and spear, dealing slashing and piercing
    damage, while also creating hazardous walls. Arx is vulnerable to: Low Dexterity
    makes it vulnerable to ranged attacks. '
  - 'Dragon Cultist is found in the following environments: Can be found in places
    where dragon cults have taken root. Dragon Cultist is connected to: Related to
    other dragon cultists and dragons. Dragon Cultist is driven by: To serve their
    dragon masters and spread their influence. '
- source_sentence: huge construct with a heated body
  sentences:
  - 'Mold Zombie is described as: The Mold Zombie is a decaying figure draped in fungal
    growths, exuding a foul odor. Its skin is rotting, and it is often surrounded
    by clouds of spores. Mold Zombie is remarkable for: Its ability to explode in
    spores upon death and spread disease makes it particularly terrifying. '
  - 'Zalikum is situated in: Typically found in hostile environments, particularly
    deserts or locations of death and decay. Zalikum is connected to: May serve a
    powerful creator or be encountered alongside other constructs. Zalikum is focused
    on: To eliminate enemies and store their souls for rejuvenation. '
  - 'Here are some interesting facts about Stellar Rorqual: Mouth Compartment offers
    total cover and environmental control for creatures inside. Planar Dive ability
    allows strategic teleportation to various planes. Blindsight enhances its combat
    awareness even in total darkness. Weakness to force damage can be exploited in
    combat. Highly mobile with significant flying and swimming speeds. '
- source_sentence: aquatic creature that avoids reptilian humanoids
  sentences:
  - 'Here are some interesting facts about Grimmlet: Immunities to multiple conditions,
    making it resilient in various situations. Can cast spells without needing components,
    leveraging psionics. Explodes upon death, dealing psychic damage to nearby foes. '
  - 'Ancient Mithral Dragon is located in: Usually found in mountainous regions, ancient
    ruins, or secluded lairs that serve as its domain. Ancient Mithral Dragon has
    the following relations: It may command lesser dragons or allied creatures and
    could be sought after by powerful spellcasters for its magic-resistant qualities.
    Ancient Mithral Dragon is focused on: To assert dominance over its territory,
    use its intellect in combat, and protect its hoard from intruders. '
  - 'Useful tidbits about Spinosaurus: Can hold its breath for up to 1 hour, making
    it formidable in water. Deals double damage to objects and structures as a Siege
    Monster. Can take legendary actions to move or attack between other creatures''
    turns. '
- source_sentence: haunting entity lurking in dark places
  sentences:
  - 'Useful tidbits about Wraith Bear: Immune to necrotic and poison damage Condition
    immunity to charm and paralysis Can move through objects as difficult terrain
    Draining regeneration destroys nearby plants Life drain potentially reduces maximum
    Hit Points. '
  - 'Faceless Wanderer is referred to as: The Faceless Wanderer appears as a shifting,
    formless entity, lacking any facial features or distinct form, making it unsettling
    to behold. It has a ghostly presence and floats through the air, leaving a chilling
    aura. Faceless Wanderer is memorable for: Notably drains memories and can cause
    targets to forget encounters with it, posing a unique threat to adventurers. '
  - 'Giant Snow Beetle is proficient in: Strong physical attacks combined with stealth
    capabilities and environmental manipulation. Giant Snow Beetle boasts: Proficient
    in athletics and stealth, making it a formidable ambusher. Giant Snow Beetle has
    the following most powerful ability: Rotten Snowball Shove allows it to poison
    and damage multiple targets simultaneously. Giant Snow Beetle can use: Pincer
    attack deals bludgeoning damage, while snowball attacks can cause damage, knockdown
    effects, and poison. Giant Snow Beetle is vulnerable to: Very low intelligence
    and charisma, making it less effective in social interactions. '
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer

This is a [sentence-transformers](https://www.SBERT.net) model trained. It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 512 tokens
- **Output Dimensionality:** 384 tokens
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 512, 'do_lower_case': False}) with Transformer model: BertModel 
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'haunting entity lurking in dark places',
    'Faceless Wanderer is referred to as: The Faceless Wanderer appears as a shifting, formless entity, lacking any facial features or distinct form, making it unsettling to behold. It has a ghostly presence and floats through the air, leaving a chilling aura. Faceless Wanderer is memorable for: Notably drains memories and can cause targets to forget encounters with it, posing a unique threat to adventurers. ',
    'Useful tidbits about Wraith Bear: Immune to necrotic and poison damage Condition immunity to charm and paralysis Can move through objects as difficult terrain Draining regeneration destroys nearby plants Life drain potentially reduces maximum Hit Points. ',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities.shape)
# [3, 3]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset


* Size: 172,300 training samples
* Columns: <code>anchor</code>, <code>positive</code>, and <code>negative</code>
* Approximate statistics based on the first 1000 samples:
  |         | anchor                                                                           | positive                                                                            | negative                                                                            |
  |:--------|:---------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
  | type    | string                                                                           | string                                                                              | string                                                                              |
  | details | <ul><li>min: 4 tokens</li><li>mean: 8.53 tokens</li><li>max: 16 tokens</li></ul> | <ul><li>min: 32 tokens</li><li>mean: 85.31 tokens</li><li>max: 201 tokens</li></ul> | <ul><li>min: 32 tokens</li><li>mean: 84.01 tokens</li><li>max: 195 tokens</li></ul> |
* Samples:
  | anchor                                                       | positive                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | negative                                                                                                                                                                                                                                                                                                                                                                                                                            |
  |:-------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>small evil creature with amphibious abilities</code>   | <code>Cueyatl Warchief is found in the following environments: Primarily found in jungle terrains, where it utilizes camouflage. Cueyatl Warchief is associated with: Can communicate with insectoid creatures and may lead other jungle inhabitants. Cueyatl Warchief has the following goals: To lead and command allies in battle, utilizing its amphibious and jungle abilities. </code>                                                                                                                                  | <code>Here are some interesting facts about Wardu: Immune to exhaustion and the prone condition. Regains hit points equal to half the damage dealt with its proboscis attack. Has Flyby ability to avoid opportunity attacks while flying. Magic Resistance provides advantage on saving throws against spells. Targets attacked may suffer disadvantage on concentration checks if they are spellcasters. </code>                  |
  | <code>tiny creature with horrifying visions in combat</code> | <code>Gloomflower is skilled in: High Charisma allows it to strongly influence foes through telepathy and psychic effects. Gloomflower can execute: Corrupting Visions, which inflicts ongoing psychic damage and forces foes to attack others. Gloomflower has the following attacks: The Gloomflower makes psychic strikes from a distance, dealing significant psychic damage with its multiattack. Gloomflower is not good at: Low Dexterity and Intelligence scores limit its agility and tactical capabilities. </code> | <code>Mycolid Commoner is found in the following environments: Typically inhabits forested or overgrown areas rich in decaying vegetation. Mycolid Commoner is linked to: Often found in communities with other Mycolids. Mycolid Commoner is driven by: To support its kin and maintain stealth within its ecosystem. </code>                                                                                                      |
  | <code>formidable fire-absorbing humanoid</code>              | <code>Useful tidbits about Ouroban: Immune to fire damage and cannot be poisoned. Uses necrotic damage in addition to its regular attacks after using its Devastate ability. Has a variety of control spells, enhancing its presence in battle. Fire Breath attack that can damage multiple targets. A tactical spellcaster with potent area control abilities. </code>                                                                                                                                                       | <code>Ogre, Cunning Artisan is present in: Usually found in areas rich with magical artifacts or in places where it can enhance its craft. Ogre, Cunning Artisan is connected to: Often found with other giants or magical creatures, it can serve as an antagonist or a formidable ally. Ogre, Cunning Artisan is driven by: Typically looking to dominate weaker foes and manipulate magical items for its own advantage. </code> |
* Loss: [<code>TripletLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#tripletloss) with these parameters:
  ```json
  {
      "distance_metric": "TripletDistanceMetric.COSINE",
      "triplet_margin": 0.3
  }
  ```

### Evaluation Dataset

#### Unnamed Dataset


* Size: 21,000 evaluation samples
* Columns: <code>anchor</code>, <code>positive</code>, and <code>negative</code>
* Approximate statistics based on the first 1000 samples:
  |         | anchor                                                                           | positive                                                                            | negative                                                                            |
  |:--------|:---------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
  | type    | string                                                                           | string                                                                              | string                                                                              |
  | details | <ul><li>min: 4 tokens</li><li>mean: 8.62 tokens</li><li>max: 15 tokens</li></ul> | <ul><li>min: 35 tokens</li><li>mean: 83.24 tokens</li><li>max: 203 tokens</li></ul> | <ul><li>min: 37 tokens</li><li>mean: 85.79 tokens</li><li>max: 195 tokens</li></ul> |
* Samples:
  | anchor                                                          | positive                                                                                                                                                                                                                                                                                                               | negative                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
  |:----------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>monster immune to necrotic damage</code>                  | <code>Useful tidbits about Nullicorn: Immunities to necrotic and poison damage. Resistance to being charmed, paralyzed, or poisoned. Magic Resistance provides advantage on saving throws against magical effects. Ability to sense magic within a 120 ft radius. </code>                                              | <code>Nharyth has the following strengths: High resilience with substantial hit points and several resistances; immune to conditions that would hinder its combat effectiveness. Nharyth is capable of: Excels in perception and stealth, making it a formidable ambusher. Nharyth can unleash: The devastating Spine Trap, which can create hazardous terrain that ensnares and paralyzes enemies. Nharyth can perform: Utilizes multiattack options with powerful spined slap and ranged spine shot attacks, able to inflict paralysis on hitting opponents. Nharyth is susceptible to: Low Intelligence and Charisma suggest vulnerability in mental challenges and social interactions. </code>                                                                                                |
  | <code>dark creature with powerful incapacitating ability</code> | <code>Dark Eye is present in: Typically found in dark or shadowy locations, avoiding sunlight. Dark Eye has the following relations: Related to other shadowy humanoids or creatures that thrive in darkness. Dark Eye is focused on: To control and dominate opponents using manipulation and combat prowess. </code> | <code>Interesting facts about Scribe Devil: Can cast detect magic and illusory script at will. Benefits from magical resistance, enhancing its durability. Can set traps using glyph of warding. Capable of enforcing truth with zone of truth. Claw attacks can inflict significant melee damage. </code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
  | <code>manipulative dragon capable of sonic attacks</code>       | <code>Interesting facts about Zilaq: Ability to create illusory creatures with Phantasmal Oratory for tactical deception. Can charm multiple creatures and cause chaos with Enthralling Speech. Remarkable strategic presence due to a combination of mobility and spell-like abilities. </code>                       | <code>Amethyst Dragon Wyrmling is strong in: Resistance to force and psychic damage, immunity to fatigue, and strong telepathic communication. Amethyst Dragon Wyrmling has the following skills: Proficient in deception and persuasion, reflecting its capabilities in social encounters. Amethyst Dragon Wyrmling can use: Far Thoughts allows the dragon to observe any creature using psionic abilities or communicating telepathically within 100 miles. Amethyst Dragon Wyrmling can use: Can make a melee attack with a bite that deals considerable piercing damage and unleash a 'Concussive Breath' attack that affects multiple foes with psionic energy. Amethyst Dragon Wyrmling is susceptible to: Average physical attributes with no exceptional strengths or weaknesses. </code> |
* Loss: [<code>TripletLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#tripletloss) with these parameters:
  ```json
  {
      "distance_metric": "TripletDistanceMetric.COSINE",
      "triplet_margin": 0.3
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `overwrite_output_dir`: True
- `eval_strategy`: epoch
- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 64
- `weight_decay`: 0.02
- `lr_scheduler_type`: cosine
- `warmup_steps`: 1615
- `load_best_model_at_end`: True

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: True
- `do_predict`: False
- `eval_strategy`: epoch
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 64
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.02
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1.0
- `num_train_epochs`: 3
- `max_steps`: -1
- `lr_scheduler_type`: cosine
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 1615
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: True
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: False
- `hub_always_push`: False
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `dispatch_batches`: None
- `split_batches`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `eval_use_gather_object`: False
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional

</details>

### Training Logs
<details><summary>Click to expand</summary>

| Epoch   | Step     | Training Loss | loss       |
|:-------:|:--------:|:-------------:|:----------:|
| 0.0186  | 100      | 0.2623        | -          |
| 0.0371  | 200      | 0.1973        | -          |
| 0.0557  | 300      | 0.1447        | -          |
| 0.0743  | 400      | 0.1242        | -          |
| 0.0929  | 500      | 0.114         | -          |
| 0.1114  | 600      | 0.1077        | -          |
| 0.1300  | 700      | 0.1052        | -          |
| 0.1486  | 800      | 0.0978        | -          |
| 0.1671  | 900      | 0.0939        | -          |
| 0.1857  | 1000     | 0.0904        | -          |
| 0.2043  | 1100     | 0.0855        | -          |
| 0.2228  | 1200     | 0.0818        | -          |
| 0.2414  | 1300     | 0.0815        | -          |
| 0.2600  | 1400     | 0.0738        | -          |
| 0.2786  | 1500     | 0.0709        | -          |
| 0.2971  | 1600     | 0.0706        | -          |
| 0.3157  | 1700     | 0.067         | -          |
| 0.3343  | 1800     | 0.067         | -          |
| 0.3528  | 1900     | 0.0652        | -          |
| 0.3714  | 2000     | 0.0589        | -          |
| 0.3900  | 2100     | 0.0531        | -          |
| 0.4085  | 2200     | 0.0541        | -          |
| 0.4271  | 2300     | 0.0511        | -          |
| 0.4457  | 2400     | 0.0443        | -          |
| 0.4643  | 2500     | 0.0464        | -          |
| 0.4828  | 2600     | 0.0462        | -          |
| 0.5014  | 2700     | 0.0417        | -          |
| 0.5200  | 2800     | 0.0425        | -          |
| 0.5385  | 2900     | 0.0421        | -          |
| 0.5571  | 3000     | 0.037         | -          |
| 0.5757  | 3100     | 0.0345        | -          |
| 0.5942  | 3200     | 0.0354        | -          |
| 0.6128  | 3300     | 0.0349        | -          |
| 0.6314  | 3400     | 0.0352        | -          |
| 0.6500  | 3500     | 0.0305        | -          |
| 0.6685  | 3600     | 0.0346        | -          |
| 0.6871  | 3700     | 0.028         | -          |
| 0.7057  | 3800     | 0.0276        | -          |
| 0.7242  | 3900     | 0.028         | -          |
| 0.7428  | 4000     | 0.0273        | -          |
| 0.7614  | 4100     | 0.0261        | -          |
| 0.7799  | 4200     | 0.0267        | -          |
| 0.7985  | 4300     | 0.0237        | -          |
| 0.8171  | 4400     | 0.0231        | -          |
| 0.8357  | 4500     | 0.0224        | -          |
| 0.8542  | 4600     | 0.0205        | -          |
| 0.8728  | 4700     | 0.0213        | -          |
| 0.8914  | 4800     | 0.0217        | -          |
| 0.9099  | 4900     | 0.02          | -          |
| 0.9285  | 5000     | 0.02          | -          |
| 0.9471  | 5100     | 0.0195        | -          |
| 0.9656  | 5200     | 0.0167        | -          |
| 0.9842  | 5300     | 0.0181        | -          |
| **1.0** | **5385** | **-**         | **0.1767** |
| 1.0028  | 5400     | 0.0171        | -          |
| 1.0214  | 5500     | 0.0126        | -          |
| 1.0399  | 5600     | 0.01          | -          |
| 1.0585  | 5700     | 0.0109        | -          |
| 1.0771  | 5800     | 0.0125        | -          |
| 1.0956  | 5900     | 0.0106        | -          |
| 1.1142  | 6000     | 0.0119        | -          |
| 1.1328  | 6100     | 0.0119        | -          |
| 1.1513  | 6200     | 0.0101        | -          |
| 1.1699  | 6300     | 0.0096        | -          |
| 1.1885  | 6400     | 0.0113        | -          |
| 1.2071  | 6500     | 0.0094        | -          |
| 1.2256  | 6600     | 0.0095        | -          |
| 1.2442  | 6700     | 0.0102        | -          |
| 1.2628  | 6800     | 0.009         | -          |
| 1.2813  | 6900     | 0.0085        | -          |
| 1.2999  | 7000     | 0.008         | -          |
| 1.3185  | 7100     | 0.0093        | -          |
| 1.3370  | 7200     | 0.0076        | -          |
| 1.3556  | 7300     | 0.0086        | -          |
| 1.3742  | 7400     | 0.0081        | -          |
| 1.3928  | 7500     | 0.0083        | -          |
| 1.4113  | 7600     | 0.0079        | -          |
| 1.4299  | 7700     | 0.0068        | -          |
| 1.4485  | 7800     | 0.0062        | -          |
| 1.4670  | 7900     | 0.007         | -          |
| 1.4856  | 8000     | 0.0057        | -          |
| 1.5042  | 8100     | 0.0068        | -          |
| 1.5227  | 8200     | 0.0084        | -          |
| 1.5413  | 8300     | 0.0067        | -          |
| 1.5599  | 8400     | 0.0055        | -          |
| 1.5785  | 8500     | 0.0064        | -          |
| 1.5970  | 8600     | 0.006         | -          |
| 1.6156  | 8700     | 0.0061        | -          |
| 1.6342  | 8800     | 0.0059        | -          |
| 1.6527  | 8900     | 0.0052        | -          |
| 1.6713  | 9000     | 0.0051        | -          |
| 1.6899  | 9100     | 0.0053        | -          |
| 1.7084  | 9200     | 0.0052        | -          |
| 1.7270  | 9300     | 0.005         | -          |
| 1.7456  | 9400     | 0.0034        | -          |
| 1.7642  | 9500     | 0.004         | -          |
| 1.7827  | 9600     | 0.0042        | -          |
| 1.8013  | 9700     | 0.0041        | -          |
| 1.8199  | 9800     | 0.0042        | -          |
| 1.8384  | 9900     | 0.0039        | -          |
| 1.8570  | 10000    | 0.0029        | -          |
| 1.8756  | 10100    | 0.0031        | -          |
| 1.8942  | 10200    | 0.0033        | -          |
| 1.9127  | 10300    | 0.0024        | -          |
| 1.9313  | 10400    | 0.0027        | -          |
| 1.9499  | 10500    | 0.0032        | -          |
| 1.9684  | 10600    | 0.003         | -          |
| 1.9870  | 10700    | 0.0031        | -          |
| 2.0     | 10770    | -             | 0.1883     |
| 2.0056  | 10800    | 0.0023        | -          |
| 2.0241  | 10900    | 0.0017        | -          |
| 2.0427  | 11000    | 0.0021        | -          |
| 2.0613  | 11100    | 0.0013        | -          |
| 2.0799  | 11200    | 0.0014        | -          |
| 2.0984  | 11300    | 0.0013        | -          |
| 2.1170  | 11400    | 0.0014        | -          |
| 2.1356  | 11500    | 0.0016        | -          |
| 2.1541  | 11600    | 0.0014        | -          |
| 2.1727  | 11700    | 0.0015        | -          |
| 2.1913  | 11800    | 0.001         | -          |
| 2.2098  | 11900    | 0.0013        | -          |
| 2.2284  | 12000    | 0.0014        | -          |
| 2.2470  | 12100    | 0.001         | -          |
| 2.2656  | 12200    | 0.0015        | -          |
| 2.2841  | 12300    | 0.0009        | -          |
| 2.3027  | 12400    | 0.0014        | -          |
| 2.3213  | 12500    | 0.0011        | -          |
| 2.3398  | 12600    | 0.0011        | -          |
| 2.3584  | 12700    | 0.001         | -          |
| 2.3770  | 12800    | 0.0007        | -          |
| 2.3955  | 12900    | 0.0013        | -          |
| 2.4141  | 13000    | 0.001         | -          |
| 2.4327  | 13100    | 0.0011        | -          |
| 2.4513  | 13200    | 0.0012        | -          |
| 2.4698  | 13300    | 0.0008        | -          |
| 2.4884  | 13400    | 0.0008        | -          |
| 2.5070  | 13500    | 0.0009        | -          |
| 2.5255  | 13600    | 0.001         | -          |
| 2.5441  | 13700    | 0.0009        | -          |
| 2.5627  | 13800    | 0.0011        | -          |
| 2.5812  | 13900    | 0.0007        | -          |
| 2.5998  | 14000    | 0.0004        | -          |
| 2.6184  | 14100    | 0.0008        | -          |
| 2.6370  | 14200    | 0.0008        | -          |
| 2.6555  | 14300    | 0.0009        | -          |
| 2.6741  | 14400    | 0.0008        | -          |
| 2.6927  | 14500    | 0.0007        | -          |
| 2.7112  | 14600    | 0.0005        | -          |
| 2.7298  | 14700    | 0.0007        | -          |
| 2.7484  | 14800    | 0.0005        | -          |
| 2.7669  | 14900    | 0.0005        | -          |
| 2.7855  | 15000    | 0.0008        | -          |
| 2.8041  | 15100    | 0.0007        | -          |
| 2.8227  | 15200    | 0.0007        | -          |
| 2.8412  | 15300    | 0.0006        | -          |
| 2.8598  | 15400    | 0.0006        | -          |
| 2.8784  | 15500    | 0.0005        | -          |
| 2.8969  | 15600    | 0.0008        | -          |
| 2.9155  | 15700    | 0.0011        | -          |
| 2.9341  | 15800    | 0.0007        | -          |
| 2.9526  | 15900    | 0.0009        | -          |
| 2.9712  | 16000    | 0.0004        | -          |
| 2.9898  | 16100    | 0.0007        | -          |
| 3.0     | 16155    | -             | 0.1962     |

* The bold row denotes the saved checkpoint.
</details>

### Framework Versions
- Python: 3.10.5
- Sentence Transformers: 3.1.1
- Transformers: 4.45.2
- PyTorch: 2.4.1+cu124
- Accelerate: 1.0.0
- Datasets: 3.0.1
- Tokenizers: 0.20.0

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### TripletLoss
```bibtex
@misc{hermans2017defense,
    title={In Defense of the Triplet Loss for Person Re-Identification},
    author={Alexander Hermans and Lucas Beyer and Bastian Leibe},
    year={2017},
    eprint={1703.07737},
    archivePrefix={arXiv},
    primaryClass={cs.CV}
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->