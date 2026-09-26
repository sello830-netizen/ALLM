# Multi-View Pilot v0

## الهدف

اختبار ما إذا كان masked-span self-supervision يضيف إشارة مفيدة من نفس النص الأصلي دون ادعاء أنه يخلق معلومات جديدة.

لا نستخدم LLM خارجيًا ولا نولد QA/relations غير موثقة؛ البيانات الحالية synthetic ولا تحتوي annotations دلالية.

## الحالات

1. `original`: النص الأصلي فقط.
2. `one_view_per_source`: view واحدة حتمية لكل مصدر؛ ضابط يساوي عدد المصادر، لكنه ليس token-matched تمامًا.
3. `multiview`: النص الأصلي + masked-span view لكل مصدر؛ يزيد عدد الأمثلة والـtokens.

الـmasked view تكون بصيغة:

```text
TASK_MASK prefix MASK_TOKEN suffix TARGET_TOKEN span
```

وهي view ذاتية مشتقة من النص، وليست paraphrase أو حقيقة جديدة.

## البناء

```text
python scripts/build_multiview_pilot.py \
  data/fixtures/arabic_baseline_corpus_500.jsonl \
  data/fixtures/arabic_baseline_corpus_500_multiview \
  --seed 17
```

الـmanifest يسجل token budget لكل حالة. في النسخة الحالية يجب عدم تفسير `multiview` كـsame-token comparison؛ نقارن نفس `max_steps` و`batch_size`، ونفصل أثر views عن أثر compute في التقرير.

## التشغيل على Colab

```python
!git -C /content/ALLM pull --ff-only
%cd /content/ALLM
!python scripts/build_multiview_pilot.py data/fixtures/arabic_baseline_corpus_500.jsonl data/fixtures/arabic_baseline_corpus_500_multiview --seed 17
```

ثم نشغل `one_view` و`multiview` بنفس:

```text
max_steps=500
batch_size=4
seed=17
architecture ثابتة
```

يجب حفظ كل run في registry مختلف أو بنفس registry مع `run_id` الجديد، وعدم حذف السجلات السابقة.

## حدود القرار

لا تُعتبر Multi-View ناجحة إلا إذا تحسنت dev known-token metrics أو structural metrics، مع فحص OOV، وعدم اعتماد النتيجة على زيادة الـtokens وحدها. لا تستخدم هذه التجربة لإثبات جودة نموذج عربي عام.
