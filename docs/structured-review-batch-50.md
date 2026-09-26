# Structured Review Batch 50

## الهدف

توسيع الـstructured annotation من 11 سجلًا إلى batch متوازن: سجلان على الأقل من كل domain من الـ25 domain، مع الحفاظ على كل annotations الموجودة حتى لو تجاوز العدد 50 قليلًا، ودون اعتماد تلقائي أو اختلاق labels.

الأداة:

```text
python scripts/prepare_structured_review_batch.py \
  data/fixtures/arabic_baseline_corpus_500.jsonl \
  data/fixtures/structured_micro_pilot_proposed.jsonl \
  data/fixtures/structured_review_batch_50.jsonl \
  --per-domain 2 \
  --seed 17
```

## سياسة الاعتماد

- annotations الموجودة تُحفظ بحالتها.
- السجلات الجديدة تبدأ `proposed_needs_review`.
- لا تدخل أي annotation التدريب قبل مراجعتها.
- لا تستخدم `--allow-proposed` كحل لتجاوز البوابة.

## ما يجب مراجعته لكل سجل

- relations مستندة إلى النص.
- events والـarguments.
- state transitions الصريحة فقط.
- temporal order المذكور أو الواضح مباشرة.
- causal claims الصريحة، لا الاستنتاجات الخارجية.

بعد اكتمال المراجعة، شغّل validator ثم structured split. هذه العينة تصلح لـmicro-pilot، لا لادعاء جودة نموذج عربي عام.
