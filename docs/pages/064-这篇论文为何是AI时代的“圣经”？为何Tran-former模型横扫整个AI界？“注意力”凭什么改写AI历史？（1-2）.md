---
layout: article
title: 这篇论文为何是AI时代的“圣经”？为何Tran-former模型横扫整个AI界？“注意力”凭什么改写AI历史？（1-2）
permalink: /pages/064-这篇论文为何是AI时代的“圣经”？为何Tran-former模型横扫整个AI界？“注意力”凭什么改写AI历史？（1-2）/
page_num: 64
section_id: '06'
section_name: 案例与参考
section_slug: cases-and-refs
ord: '06.9'
read_min: 18
word_count: 8237
is_featured: false
prev_url: /pages/063-关于AI联网搜索是如何实现的，细品，精华巨多。解读OpenAI出品的《WebGPT》（2-2）/
prev_title: 关于AI联网搜索是如何实现的，细品，精华巨多。解读OpenAI出品的《WebGPT》（2-2）
next_url: /pages/065-这篇论文为何是AI时代的“圣经”？为何Tran-former模型横扫整个AI界？“注意力”凭什么改写AI历史？（2-2）/
next_title: 这篇论文为何是AI时代的“圣经”？为何Tran-former模型横扫整个AI界？“注意力”凭什么改写AI历史？（2-2）
---

下面我们一起来学习，这篇开创了现代人工智能新纪元的论文——《Attention Is All You Need》。

![image]()

我会将这篇论文分解成几个部分，逐一为你讲解。用通俗的语言解释核心概念，同时保留其专业性，确保你既能理解“它是什么”，也能明白“它为什么重要”。

在我们开始之前，先做一个高层次的总结：

- •论文名称: Attention Is All You
Need（注意力就是你所需要的一切）

- •核心贡献: 提出了Transformer模型架构。

- •革命性思想: 完全抛弃了之前处理序列数据（如文本）最主流的循环神经网络（RNN）和卷积神经网络（CNN），证明了仅仅依靠**注意力机制（Attention Mechanism）**就可以在任务上做得更好、训练得更快。

- •历史地位: 这篇论文是AI领域的分水岭。我们今天所熟知的几乎所有大型语言模型，比如 GPT系列、BERT、Claude系列、DeepSeek、Llama，其底层架构都源于这篇论文提出的 Transformer。

现在，让我们一页一页地深入探索。

---

第一页：标题、作者与摘要 (Title, Authors & Abstract)

标题与作者

- •Attention Is All You Need: 这个标题非常自信且具有冲击力。它直接点明了论文的核心论点：在处理序列信息时，你不再需要过去那些复杂的结构，"注意力"就足够了。

- •作者团队: 作者基本都来自 Google Brain 和 Google Research，还有一个来自多伦多大学。值得注意的是，作者列表下的*Equal contribution（同等贡献）和随机排序，表明这是一个紧密合作的团队项目。

摘要 (Abstract)

摘要是整篇论文的浓缩精华。我们来逐句解析：

The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder.

- •讲解:

- •Sequence Transduction Models (序列转导模型): 这是什么？简单来说，就是输入一个序列，输出另一个序列的模型。最经典的例子就是机器翻译：输入一句德语（序列1），输出一句英语（序列2）。

- •Recurrent (RNN) or Convolutional (CNN) Neural Networks: 在这篇论文之前，处理序列数据的王者是循环神经网络(RNN)。你可以把RNN想象成一个有短期记忆的人，在读一个句子时，他会一个词一个词地读，并且努力记住前面词的信息。但RNN有个大问题：当句子很长时，它很容易“遗忘”最开始的信息。而且，它必须一个词一个词按顺序处理，无法并行计算，速度很慢。

- •Encoder-Decoder (编码器-解码器): 这是一个很流行的架构。想象一个同声传译员。他先听完一整句德语（编码器的工作，理解并浓缩成一种“意思”），然后再根据这个“意思”说出对应的英语（解码器的工作，生成新句子）。当时的顶尖模型都是基于“RNN编码器 + RNN解码器”的。

We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.

- •讲解: 这是论文的核心宣言。

- •We propose... the Transformer: 我们提出了一个新的、更简单的架构，名叫“Transformer”。

- •based solely on attention mechanisms: 它的基石只有注意力机制。

- •dispensing with recurrence... entirely: 它完全抛弃了前面提到的RNN那种按顺序处理的“循环”结构。这是一个颠覆性的举动。

Experiments on two machine translation tasks show these models to be superior in quality... more parallelizable and requiring significantly less time to train.

- •讲解: 论文亮出了成果。

- •Superior in quality: 效果更好。

- •More parallelizable: 因为没有了RNN那种必须按顺序处理的限制，模型可以同时处理句子中的所有词，极大地提高了计算效率。这就像以前只能走单车道，现在直接上了八车道高速公路。

- •Less time to train: 训练时间显著缩短。

Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU.

- •讲解: 具体的战绩。

- •BLEU: 是一种评估机器翻译质量的常用指标，分数越高越好。

- •improving... by over 2 BLEU: 在当时的机器翻译领域，提升0.5个BLEU点都算很不错的进展了。一下子提升超过2.0个点，而且是超越了当时最强的多个模型集成（ensembles）的结果，这是非常惊人的突破，足以震动整个学术界。

小结 (Page 1)

第一页就告诉我们：过去，我们用一种叫RNN的慢速、顺序的方法做机器翻译等任务。现在，我们发明了“Transformer”，它只用“注意力”机制，不仅做得更好，而且速度快得多。我们用惊人的实验结果证明了这一点。

---

第二页：背景与模型架构介绍 (Background & Model Architecture)

背景 (Background)

Recurrent models typically factor computation along the symbol positions... This inherently sequential nature precludes parallelization within training examples...

•讲解: 这里详细阐述了之前提到的RNN的最大痛点——顺序依赖性。RNN在处理句子 "我爱人工智能" 时，必须先处理 "我"，再处理 "爱"，再处理 "人工智能"。这个过程是串行的，就像一条生产线，上一道工序没完成，下一道就不能开始。这在拥有强大并行计算能力的现代硬件（如GPU）上是巨大的浪费。

Attention mechanisms have become an integral part... allowing modeling of dependencies without regard to their distance...

•讲解: 作者提到，注意力机制本身不是他们发明的。在Transformer之前，注意力通常是作为RNN的“辅助插件”使用的。它的好处是可以建立长距离依赖关系。

•什么是长距离依赖？比如这个句子：“我在法国长大，......，所以我能说一口流利的法语。” “法语”和“法国”之间的关系非常紧密，但它们在句子中相隔很远。RNN很难捕捉到这种远距离关系，但注意力机制可以轻松做到，因为它能直接看到句子里的所有词，并评估它们之间的相关性。

To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention...

•讲解: 作者再次强调了他们的首创性：虽然注意力不新，但我们是第一个完全只用注意力，而彻底抛弃RNN和CNN来做序列转导任务的模型。

模型架构 (Model Architecture)

Most competitive neural sequence transduction models have an encoder-decoder structure... The Transformer follows this overall architecture...

•讲解: Transformer整体上依然遵循经典的编码器-解码器（Encoder-Decoder）框架。你可以把这个框架想象成两个部分：

1.编码器 (Encoder): 左半部分。它的任务是“阅读”和“理解”输入的整个句子。比如输入德语“Ich bin ein Student”，编码器会处理这句话，并为每个词生成一个富含上下文信息的表示（或称“向量”）。

2.解码器 (Decoder): 右半部分。它的任务是“生成”目标句子。它会一个词一个词地生成英语 "I am a student"。在生成每个词的时候，它不仅会参考自己已经生成的词（比如生成 "a" 时会看前面的 "I am"），还会去查看编码器对整个德语句子的理解，以确保翻译的准确性。

Encoder: The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network.

•讲解:

•N = 6 identical layers: 编码器不是一个单层结构，而是由6个完全相同的层堆叠而成。就像盖楼，一层一层往上加，每一层都会对信息进行更深层次的加工。

•Two sub-layers: 每一层内部又包含两个关键部件：

1.Multi-head self-attention (多头自注意力): 这是Transformer的核心创新。我们稍后会详细讲。现在你可以把它理解成一个超级强大的“关系分析器”，它能分析输入句子中每个词与其他所有词的关联程度。

2.Feed-forward network (前馈网络): 你可以把它看作一个简单的处理单元。在注意力机制分析完词语间的关系、并融合了上下文信息之后，前馈网络会对每个词的表示进行一次独立的、深入的加工。

---

第三、四页：模型的核心——注意力机制 (The Core: Attention)

这两页是全篇论文最关键、最密集的部分。我们会详细拆解。

3.2.1 缩放点积注意力 (Scaled Dot-Product Attention)

这是Transformer使用的注意力机制的具体实现。

An attention function can be described as mapping a query and a set of key-value pairs to an output...

•讲解: 作者用三个概念来描述注意力：查询(Query, Q),键(Key, K),值(Value, V)。这是一个非常精彩的类比，源于信息检索系统。

•类比: 想象你在YouTube上搜索视频。

• 你在搜索框输入的词是Query(你想查什么)。

• YouTube数据库里每个视频的标题、描述是Key(用来被你匹配的标签)。

• 视频本身就是Value(你最终想要得到的内容)。

•工作流程:

1. 你的Query会和数据库里所有的Key进行匹配，计算一个相似度分数。

2. 相似度越高的Key，它对应的Value(视频) 就会被赋予越高的权重。

3. 你最终得到的搜索结果，就是所有视频（Value）根据这个权重进行加权求和的结果。换句话说，最相关的视频排在最前面。

在Transformer的**自注意力(Self-Attention)**层，Q, K, V都来自同一个地方：上一层的输出。

•具体到句子: 对于句子 "The animal didn't cross the street because it was too tired"，当模型处理单词 "it" 的时候：

• "it" 作为Query。

• 句子中所有的词 ("The", "animal", "didn't"...) 都作为Key。

• "it" 这个Query会和所有Key计算相似度。它会发现 "animal" 和 "street" 是最可能与 "it" 相关的Key。

• 计算结果可能会发现，"animal" 的相似度分数远高于 "street"。

• 因此，"animal" 对应的Value(也就是"animal"这个词本身的含义表示) 会获得一个很高的权重，而 "street" 的Value权重就很低。

• 最后将所有词的Value根据权重加权求和，得到 "it" 这个词融合了上下文之后的新表示。在这个新表示里，"it" 的含义就强烈地指向了 "animal"。

Attention(Q, K, V) = softmax( (QK^T) / sqrt(d_k) ) * V

•讲解: 这就是注意力的计算公式。

1.QK^T:点积(Dot-Product)。计算每个Query和所有Key的相似度分数。

2./ sqrt(d_k):缩放(Scale)。d_k是Key向量的维度。这是一个小技巧，为了防止在维度很高时点积结果过大，导致后面的softmax函数梯度消失，让训练更稳定。

3.softmax: 将分数转换成总和为1的百分比权重。

4.* V: 将这个权重应用到所有的Value上，进行加权求和。

3.2.2 多头注意力 (Multi-Head Attention)

Instead of performing a single attention function... we found it beneficial to linearly project the queries, keys and values h times...

•讲解: 这是Transformer的另一个天才设计。作者发现，只用一组Q, K, V来计算注意力，就像只从一个角度去理解句子关系，可能会错过很多信息。

•类比: 想象一下，一个句子摆在你面前，让你分析它的语法、语义、指代关系等。你一个人可能会有所疏漏。

•多头注意力的解决方案: 雇佣一个专家委员会（比如，h=8个专家/头）。你不直接用原始的Q, K, V，而是为每个专家（每个头）分别创建一套专属的、简化版的Q, K, V。

• 专家1（头1）可能学会了关注主谓宾结构。

• 专家2（头2）可能学会了关注代词指代关系（就像上面的"it" -> "animal"）。

• 专家3（头3）可能学会了关注词语的同义或反义关系。

• 这8个专家（头）并行地进行各自的"缩放点积注意力"计算，得出各自的分析结果。

• 最后，将这8个专家的分析结果拼接起来，再通过一次线性变换，融合成最终的输出。

•好处: 多头注意力机制允许模型在不同的表示子空间中，从不同角度共同关注信息。这使得模型能够捕捉到更加丰富和多样的特征。

---

第五页：位置信息与网络结构 (Positional Encoding & FFN)

3.5 位置编码 (Positional Encoding)

Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens...

•讲解: 这是一个至关重要的问题。因为Transformer抛弃了RNN的顺序结构，它在计算注意力时是同时看待所有词的。在它眼里， "A B C" 和 "C B A" 没有任何区别，因为它失去了词序信息。这显然是不行的， "狗咬人" 和 "人咬狗" 的意思天差地别。

•解决方案: 在将词语输入模型之前，给每个词的**词向量(Embedding)上，加上一个位置编码(Positional Encoding)**向量。

•类比: 就像给每个参会者发一个带有座位号（比如"第1排，第3座"）的胸牌。模型看到这个胸牌，就知道这个人在哪里。

• 作者使用了一个巧妙的数学设计：用不同频率的正弦(sine)和余弦(cosine)函数来生成这个位置编码。这样做的好处是，模型不仅能知道每个词的绝对位置，还能很容易地通过线性变换推断出词语间的相对位置，而且这种编码方式可以推广到比训练时遇到的句子更长的序列。

3.3 逐位置前馈网络 (Position-wise Feed-Forward Networks)

...each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically.

•讲解: 这是编码器和解码器每个大层里的第二个子层。在多头注意力机制对上下文信息进行融合之后，信息会流经这个前馈网络。

•作用: 这个网络对每个位置的向量进行一次非线性变换，可以看作是对注意力层输出结果的进一步“消化和提炼”。它增加了模型的深度和非线性能力，使得模型能够学习更复杂的函数。

---

第六页至结尾：为何选择自注意力、训练与结论

为何选择自注意力 (Why Self-Attention)

作者在这里总结了自注意力相比于RNN和CNN的三个主要优势：

1.总计算复杂度更低: 对于序列长度n小于表示维度d的情况（这在机器翻译中很常见），自注意力的每层计算量比RNN要小。

2.可并行度更高: 自注意力的顺序操作数量是常数级别的O(1)，而RNN是O(n)。这意味着自注意力可以最大限度地利用GPU的并行计算能力，训练速度飞快。这是最核心的优势。

3.更短的长距离依赖路径: 在自注意力中，任何两个词之间的路径长度都是O(1)，它们可以直接“对话”。而在RNN中，第一个词和最后一个词需要通过n步才能建立联系，信息很容易在传递中丢失。这使得Transformer极擅长学习长距离依赖。

5-6. 训练与结果 (Training & Results)

•训练细节: 论文描述了他们使用的训练数据（WMT 2014）、硬件（8块 NVIDIA P100 GPU）、优化器（Adam）和训练时长（基础模型12小时，大模型3.5天）。这些细节展示了实现SOTA（State-of-the-art，当时最佳水平）所需的计算资源。

•结果 (Table 2): 这是论文的“战绩榜”。核心亮点是，Transformer (big)这个模型在英德翻译任务上取得了28.4的BLEU分，比之前包括谷歌自家最强的GNMT模型（26.36）在内的所有模型都要高出一大截。 而且，它的训练成本（FLOPs，浮点运算次数）远低于之前的模型。用更少的代价，取得了更好的效果，这是工业界和学术界都梦寐以求的。

结论 (Conclusion)

In this work, we presented the Transformer, the first sequence transduction model based entirely on attention...

•总结: 我们提出了Transformer，一个完全基于注意力的模型，它在翻译任务上训练更快，效果更好。

We are excited about the future of attention-based models and plan to apply them to other tasks.

•展望: 作者对这个模型的未来充满期待，并计划将其应用到文本之外的其他领域，如图像、音频和视频。这个展望在今天已经完全实现，Transformer架构已经统一了AI的多个领域。

全篇总结与历史回响

《Attention Is All You Need》之所以成为一篇“神作”，不仅仅是因为它在机器翻译上取得了技术突破，更是因为它提出了一种全新的、可扩展的、高度并行的计算范式。

•抛弃顺序依赖: 它解放了模型处理序列数据的能力，使其能完美契合现代硬件。

•注意力成为核心: 它证明了“关系建模”（通过注意力）比“顺序记忆”（通过RNN）更基本、更强大。

•奠定基础: 它所设计的Transformer架构，经过后续的演化（如BERT模型的双向编码器，GPT模型的单向解码器），成为了今天几乎所有大型语言模型（LLMs）和生成式AI的基石。

学习这篇论文，就像是回到了一个伟大时代的开端。它不仅是一个模型，更是一种思想的胜利。希望这次逐页学习能帮助你深刻理解它的精髓。