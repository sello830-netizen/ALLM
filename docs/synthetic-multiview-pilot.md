# Synthetic Multi-View Pilot v0

## الحالة

هذا dataset من 35 جملة عربية مترابطة، مصدره `synthetic` ومخصص لاختبار pipeline والفكرة، وليس دليلًا على جودة نموذج عربي عام.

الملفات:

- `data/fixtures/arabic_multiview_pilot_001.json`: المصدر المنظم مع `source_id`.
- `data/fixtures/arabic_multiview_pilot_001.txt`: export newline-delimited للتدريب الأصلي.

## التحقق

```text
python scripts/extract_json_dataset.py data/fixtures/arabic_multiview_pilot_001.json data/fixtures/arabic_multiview_pilot_001.txt
python scripts/run_smoke_baseline.py data/fixtures/arabic_multiview_pilot_001.txt reports/arabic-multiview-reference-runs.jsonl
```

النتيجة المرجعية الحالية:

- records: `35`
- tokens حسب tokenizer الحالي: `807`
- reference bigram mean perplexity: `229.10468786612307`

## حدود الاستنتاج

- النص مترابط وموضوعه واحد، لذلك لا يقيس diversity.
- بعض الصياغات synthetic وقد تحتاج مراجعة لغوية.
- لا توجد views مولدة بعد في هذا الإصدار.
- لا يستخدم هذا dataset لاعتماد architecture أو الادعاء بضغط البيانات.

## Original-only baseline المنضبط

تقسيم الوثائق حتمي وبـseed=17:

```text
28 train / 3 dev / 4 test
```

```text
python scripts/prepare_text_splits.py data/fixtures/arabic_multiview_pilot_001.json data/fixtures/arabic_multiview_pilot_001_split
python scripts/train_torch_baseline.py data/fixtures/arabic_multiview_pilot_001_split/train.txt runs-original-pilot.jsonl artifacts/torch-original-pilot.pt --dev-input data/fixtures/arabic_multiview_pilot_001_split/dev.txt --max-steps 100 --batch-size 4
```

الـtest لا يستخدم لاختيار النموذج. سجل التدريب الآن يتضمن `eval_oov_rate` و`eval_known_perplexity` حتى نفصل ضعف التغطية المعجمية عن خسارة الكلمات المعروفة. كما يسجل `loss` كمتوسط كل خطوات train، و`last_batch_loss` و`effective_epochs` حتى لا نخلط خسارة آخر batch مع أداء التدريب العام. الخطوة التالية هي بناء views محدودة ومتحققًا منها، ثم مقارنة original-only وmulti-view تحت نفس token/step budget.
