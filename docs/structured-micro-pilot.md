# Structured Relation/State Micro-Pilot

## الحالة

يوجد الآن 11 annotation مقترحة يدويًا على أمثلة واضحة من corpus 500. حالتها:

```text
proposed_needs_review
```

لم تدخل التدريب. هذا مقصود؛ لا نعتبر اقتراح engineering annotation gold قبل مراجعة بشرية.

الملف:

```text
data/fixtures/structured_micro_pilot_proposed.jsonl
```

## التحقق

```text
python scripts/validate_structured_annotations.py \
  data/fixtures/arabic_baseline_corpus_500.jsonl \
  data/fixtures/structured_micro_pilot_proposed.jsonl
```

## الاعتماد

بعد مراجعة كل سجل، غيّر `review_status` إلى `approved` فقط للسجلات الصحيحة. بعدها:

```text
python scripts/build_structured_views.py \
  data/fixtures/structured_micro_pilot_proposed.jsonl \
  data/fixtures/structured_micro_pilot_views
```

الأداة ترفض proposed تلقائيًا حتى لا يدخل annotation غير مراجَع في التدريب. خيار `--approved-only` يبني subset للفحص من السجلات المعتمدة فقط ويضع `training_ready=false`، أما `--allow-proposed` فللمعاينة فقط وليس للتدريب.

## تصميم المقارنة

- Original-only: النص الأصلي.
- Structured: relation/event/state serialized.
- نفس source-level split.
- نفس architecture وseed وsteps.
- Original dev/test يستخدمان لتقييم كل الحالات.
- لا تُفسر زيادة tokens كتحسن؛ يسجل كل condition token budget الخاص به.

هذه التجربة تختبر explicit supervision محدودًا، لا تدعي أن graph أو المعادلات تضيف معرفة جديدة، ولا تستخدم أرقامًا اعتباطية للكلمات أو الحروف.
