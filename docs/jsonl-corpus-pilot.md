# JSONL Baseline Corpus Pilot

## الملف

الملف الذي قدمه المستخدم `arabic_baseline_corpus_500.jsonl` يحتوي على 500 سجل synthetic موزعة بالتساوي على 25 domain، بواقع 20 سجلًا لكل domain.

## فحص الجودة الأولي

- JSON parse errors: صفر.
- IDs مكررة: صفر.
- نصوص مكررة: صفر.
- records ناقصة text/id: صفر.
- source type: `synthetic` فقط.
- token count حسب tokenizer الحالي: `4,999` تقريبًا.

## التقسيم

الأداة:

```text
python scripts/prepare_jsonl_splits.py INPUT.jsonl OUTPUT_DIR --seed 17
```

التقسيم طبقي حسب `domain`:

```text
400 train / 50 dev / 50 test
```

والتقسيم يحافظ على تمثيل المجالات في كل split، مع source IDs غير متداخلة.

## حدود الاستنتاج

هذا corpus مناسب لـbaseline وMulti-View mechanism pilot، لكنه synthetic وقصير جدًا لكل سجل. لا يستخدم لإثبات جودة نموذج عربي عام أو معرفة العالم. يجب إبقاء test خارج اختيار الإعدادات، وعدم اعتبار الصياغات synthetic مرجعًا لغويًا ذهبيًا دون مراجعة.
