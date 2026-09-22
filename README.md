# ALLM

أساس مختبر قابل لإعادة الإنتاج لبحث نماذج اللغة العربية.

## الحالة

النسخة الحالية تؤسس عقود البيانات، خط معالجة حتميًا، وسجلًا بسيطًا للتجارب، وتحتوي على bigram reference baseline لاختبار دورة التدريب والتقييم والتسجيل دون GPU. هذا baseline ليس النموذج العصبي الإنتاجي. لا تُخزّن corpora أو checkpoints داخل Git.

## الإعداد والتحقق

بعد تثبيت Python 3.10+ فعليًا:

```text
python -m pip install -e .
python scripts/validate_foundation.py
python scripts/phase1_local_check.py --output reports/phase1-local.json
```

أو مباشرة مع pytest:

```text
python -m pytest
```

## فحص الموارد

```powershell
./scripts/check_resources.ps1
```

لا يبدأ التدريب العصبي قبل اجتياز بوابة الموارد المحددة في `docs/resource-gate-v0.md`.

## Colab

يوجد دفتر جاهز في `notebooks/colab_phase1.ipynb`، وتعليمات الربط في `docs/colab.md`. يحتاج الدفتر إلى رابط مستودع GitHub؛ لا تضع الأسرار أو البيانات الخاصة داخله.

## مصادر البيانات

تُراجع المصادر عبر `configs/data/sources.json` وسياسة `docs/data-policy.md` قبل التنزيل. يمكن تشغيل:

```text
python scripts/audit_sources.py configs/data/sources.json
python scripts/validate_source_audit.py configs/data/sources.json configs/data/source_audits.json
```

كل المصادر الحالية `proposed` ومرفوضة آليًا للتدريب حتى يكتمل تدقيق الترخيص، ولكل مصدر pre-audit موثق بالأدلة. تم تجهيز OpenITI metadata pilot من 100 سجل دون تنزيل النصوص.

## المبدأ

كل dataset أو run أو metric يجب أن يرتبط بإصدار الكود والإعدادات والـhashes الخاصة بالبيانات والتقييم. لا يُعدّل run سابق؛ الإعادة تنشئ سجلًا جديدًا.
