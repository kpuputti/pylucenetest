import lucene
import sys


INDEX_DIR = 'index'


lucene.initVM()
directory = lucene.SimpleFSDirectory(lucene.File(INDEX_DIR))
analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)


def get_data():
    data = []
    with open('data.txt') as f:
        for line in f:
            line = line.decode('utf-8').strip()
            num, name = line.split('\t')
            data.append((num, name))
    return data


def index():
    writer = lucene.IndexWriter(directory, analyzer, True,
                                lucene.IndexWriter.MaxFieldLength.UNLIMITED)

    data = get_data()

    for num, name in data:
        print num, name
        doc = lucene.Document()
        doc.add(lucene.Field('id', num, lucene.Field.Store.YES,
                             lucene.Field.Index.NOT_ANALYZED))
        doc.add(lucene.Field('name', name, lucene.Field.Store.YES,
                             lucene.Field.Index.ANALYZED))
        writer.addDocument(doc)

    print 'Indexed %d persons.' % len(data)
    writer.optimize()
    writer.close()


def search(q):
    print 'Searching text "%s".' % q
    searcher = lucene.IndexSearcher(directory, True)

    query = lucene.QueryParser(lucene.Version.LUCENE_CURRENT,
                               'name', analyzer).parse(q)

    formatter = lucene.SimpleHTMLFormatter('<b>', '</b>')
    scorer = lucene.QueryScorer(query)
    highlighter = lucene.Highlighter(formatter, scorer)
    highlighter.getTextFragmenter()

    results = searcher.search(query, None, 20)
    score_docs = results.scoreDocs
    print 'Found %d hits:' % results.totalHits

    for score_doc in score_docs:
        doc = searcher.doc(score_doc.doc)
        score = score_doc.score
        name = doc['name']
        highlighted = highlighter.getBestFragment(analyzer, 'name', name)
        print '[%f]:  "%s"' % (score, highlighted)


if __name__ == '__main__':
    args = sys.argv[1:]
    n = len(args)
    if not n:
        sys.stderr.write('Invalid arguments.\n')
        sys.exit(1)
    elif args[0] == 'index':
        index()
        sys.exit(0)
    elif args[0] == 'search' and n > 1:
        q = ' '.join(args[1].strip().split())
        search(q)
        sys.exit(0)
    else:
        sys.stderr.write('Unknown command or missing parameters.\n')
        sys.exit(1)
