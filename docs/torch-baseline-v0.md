# PyTorch Tiny Baseline v0

هذا baseline عصبي صغير للتحقق من دورة `data → train → checkpoint → registry`، وليس نموذجًا إنتاجيًا.

## الإعداد الحالي

- `d_model=128`
- `nhead=4`
- طبقتان Transformer
- context length: 64
- ثلاث epochs
- يعمل على CUDA إن توفر، وإلا CPU

## تشغيل Colab

بعد نجاح بوابة المرحلة الأولى وظهور T4 عبر `nvidia-smi`:

```python
%pip install torch
!python scripts/train_torch_baseline.py data/fixtures/smoke.txt runs-colab.jsonl artifacts/torch-tiny-baseline.pt
```

يجب أن يسجل run جديدًا ويحفظ checkpoint. لا يُستخدم fixture الصغير للحكم البحثي؛ الغرض هو إثبات سلامة دورة التدريب والتتبع.

## inference من checkpoint

```python
!python scripts/generate_torch.py \
  /content/drive/MyDrive/ALLM-artifacts/torch-tiny-baseline.pt \
  "هذه" \
  --max-new-tokens 20
```

الناتج smoke-only لأن النموذج تدرب على fixture صغير؛ لا يمثل جودة العربية العامة.
