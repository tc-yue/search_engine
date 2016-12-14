# -*-coding:utf-8 -*-
from whoosh.fields import *
from whoosh.index import create_in,open_dir
from whoosh.qparser import QueryParser
from whoosh.analysis import RegexAnalyzer,Tokenizer,Token
from whoosh import  scoring
import jieba
import os
from flask import Flask,request,render_template

app = Flask(__name__)
@app.route('/', methods=['GET'])
def home():
    return render_template('form.html')
@app.route('/', methods=['POST'])
def signin():
    # 需要从request对象读取表单内容：
    resultslist=index_open(request.form['word'])
    return render_template('form.html', page_list=resultslist)

class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,keeporiginal=False, removestops=True,start_pos=0, start_char=0, mode='', **kwargs):
        # 去除停用词及标点符号
        with open('usr/stop_words_ch.txt','r')as f:
            stop_list=f.read().split('\n')
        assert isinstance(value, text_type), "%r is not unicode" % value
        t = Token(positions, chars, removestops=removestops, mode=mode,**kwargs)
        # 搜索引擎模式粉刺
        seglist=jieba.cut_for_search(value)                           #使用结巴搜索引擎模式分词库进行分词
        for w in seglist:
            if w not in stop_list:
                t.original = t.text = w
                t.boost = 1.0
                if positions:
                    t.pos=start_pos+value.find(w)
                if chars:
                    t.startchar=start_char+value.find(w)
                    t.endchar=start_char+value.find(w)+len(w)
                yield t                                               #通过生成器返回每个分词的结果token
def ChineseAnalyzer():
    return ChineseTokenizer()

def index_create():
#重点在这里，将原先的RegexAnalyzer(ur”([\u4e00-\u9fa5])|(\w+(\.?\w+)*)”),改成这句，用中文分词器代替原先的正则表达式解释器。
    analyzer=ChineseAnalyzer()
    # 列出index的所有域
    schema=Schema(title=TEXT(stored=True),path=ID(stored=True),content=TEXT(stored=True,analyzer=analyzer))
    ix=create_in('indexer',schema)
    # 将所有文本加入索引
    writer=ix.writer()
    for root,dirs,files in os.walk('data2/'):
        for file in files:
            path2=os.path.join(root,file)
            with open(path2,'r')as f:
                content2=f.read()
                title2=content2.split('\n')[0]


            writer.add_document(title=title2,path='auto.sohu.com/'+path2[6:].replace('|','/')+'.shtml',content = content2)
    writer.commit()
def index_open(word):
    resultslist=[]
    ix = open_dir('indexer')
    with ix.searcher(weighting=scoring.TF_IDF()) as search:
        # 查询时候用精确模式分词?
        parser=QueryParser('content',ix.schema).parse(word)
        print(parser)
        # 最多30个结果
        results=search.search(parser,limit=30)
        # 每个结果最多300个字符
        results.fragmenter.charlimit = 200
        for i in results:
            # 匹配高亮
            print(i.highlights('content').replace(r'">','" color="red">'))

            resultslist.append((i['path'],i['title'],i.highlights('content').replace(r'">','" style="color:red">')))
    return resultslist
def data_preprocessing():
    for root,dirs,files in os.walk('data/'):
        for file in files:
            path2=os.path.join(root,file)
            try:
                with open(path2,'rb')as f:
                    print(path2)
                    html=f.read().decode('gbk')
                    c1=re.findall(r'<title>(.+?)-',html)[0]
                    c=re.findall(r'<div class="text clear" id="contentText" collection="Y">([\s|\S]+?)<div class="editShare clear">',html)

                    c2=re.sub(r'\<[\s|\S]*?\>|\s+','',c[0])
            except Exception as e:
                print(e)
            with open('data2/'+path2[-19:],'w')as f2:
                f2.write(c1+'\n'+c2)



if __name__ == '__main__':
    app.run()
    # index_open('好车')
    # index_create()

