## 创建 scripts/ingest_rag.py

```
我已经在app.rag包写好了rag的pipeline了，你在scripts下写一个脚本ingest_rag.py，参考notebooks/n34_rag_demo.ipynb，初始化EmbeddingModel、Milvus VectorStore，然后初始化Pipeline，接着调用app.modules.product包下的service.py中的list_products方法，查询所有products，然后调用Pipeline，实现rag知识库构建。
```