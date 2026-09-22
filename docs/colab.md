# تشغيل ALLM على Colab

## المتطلبات

- مستودع GitHub عام أو خاص.
- صلاحية الوصول إلى المستودع الخاص من Colab.
- GPU من إعدادات Colab عند الحاجة؛ التوفر والحدود متغيرة.

## الخطوات

1. أنشئ مستودعًا فارغًا على GitHub، ثم اربطه بالمستودع المحلي.
2. ادفع الكود بعد ضبط هوية Git محليًا.
3. افتح `notebooks/colab_phase1.ipynb` في Colab.
4. ضع رابط المستودع في `REPO_URL`، ولا تضع token أو secret داخل الدفتر.
5. شغّل الخلايا بالترتيب.
6. راجع `reports/phase1-colab.json` و`runs-colab.jsonl`.
7. بعد ظهور T4 عبر `nvidia-smi`، شغّل خلية neural baseline لتثبيت PyTorch وحفظ `artifacts/torch-tiny-baseline.pt`.

## البيانات الخاصة

لا ترفع corpus مرخّصًا أو خاصًا إلى GitHub أو مخرجات Notebook العامة. استخدم Google Drive أو تخزينًا خاصًا، ثم مرر المسار إلى config/manifest.

## نطاق الدفتر الحالي

الدفتر يشغل بوابة المرحلة الأولى وreference baseline، ثم يتيح tiny PyTorch Transformer smoke test عند توفر T4. الـfixture الصغير لا يمثل تدريبًا بحثيًا نهائيًا.
