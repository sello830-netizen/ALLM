# سياسة البيانات v0

## الهدف

بناء corpus عربي قابل للتتبع، لا أكبر corpus ممكن. لا يُعتبر وجود النص على الإنترنت إذنًا بالتدريب أو إعادة التوزيع.

## الطبقات

1. `redistributable_train`: يسمح المصدر صراحة بالتدريب، وإعادة توزيع البيانات عند الحاجة، وتوزيع النموذج المشتق.
2. `research_only_train`: مسموح للبحث فقط؛ لا يستخدم لإصدار نموذج تجاري أو corpus قابل لإعادة التوزيع.
3. `auxiliary_annotations`: annotations صرفية/نحوية أو لغوية تستخدم لأهداف مساعدة وتحليل وتقييم.
4. `gold_evaluation`: اختبار مقفل لا يدخل التدريب أو اختيار الأوزان.

## بوابة الترخيص

لا تُقبل أي وثيقة للإدخال إلا إذا كان مصدرها مسجلًا في `configs/data/sources.json` واجتاز `LicenseGate`. الحالات `proposed` و`under_review` مرفوضة آليًا للتدريب.

الموافقة على `redistributable_train` تتطلب، بصورة صريحة:

- `commercial_training_allowed=true`.
- `redistribution_allowed=true`.
- `derived_model_allowed=true`.
- ترخيص وإصدار ومصدر قابل للمراجعة.

لا نستنتج هذه الأذونات من اسم الترخيص وحده؛ القرار يعتمد على شروط المصدر وسلسلة النسب.

## فصل البحث عن التوزيع

كل run وdataset release يحدد الطبقة. لا يخلط pipeline بين `research_only_train` و`redistributable_train` دون إصدار واضح وسياسة قرار. القرآن وOpenITI وUD لا تدخل commercial-safe set تلقائيًا؛ كل مصدر يحتاج تدقيقًا مستقلًا.

## الإصدارات

نستخدم snapshots ثابتة من Zenodo أو release tag، لا branch متغيرًا. نحفظ metadata وhashes داخل manifests، ولا نضع corpora الخام المرخصة في Git.

## الخصوصية والأمن

- لا أسرار أو tokens داخل manifests.
- لا PII غير مفحوصة.
- البيانات الخاصة تحفظ خارج GitHub وColab outputs العامة.
- أي طلب حذف أو سحب ترخيص يوقف المصدر ويُصدر dataset release جديدًا.

هذه سياسة هندسية وليست رأيًا قانونيًا؛ المصادر الحساسة تحتاج مراجعة قانونية قبل التوزيع التجاري.
