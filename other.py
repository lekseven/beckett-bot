import re

def str_keys(dict,keys,pre=''):
    ans=[]
    for key in keys:
        if key in dict:
            ans.append(pre + '[' + key + '] = ' + dict[key])
    return '\n'.join(ans) if ans else []


def comfortable_help(docs):
    lens = []
    docs2 = []
    for doc in docs:
        if doc:
            new_doc = doc.split('\n')
            docs2 += new_doc
            for doc2 in new_doc:
                lens.append(len(re.match('.*?[:]', doc2).group(0)))

    m = max(lens)
    docs = []
    for doc in docs2:
        docs.append(doc.replace(':', ':' + (' ' * (m - lens.pop(0))) + '\t'))

    docs.sort()
    #print('len(docs)=', len(docs))
    docs_len = len(docs)
    count_helps = int(docs_len / 21) + 1  # 20 lines for one message
    step = int(docs_len / count_helps - 0.001) + 1
    helps = [docs[i:i + step] for i in range(0, len(docs), step)]
    texts = []
    for h in helps:
        texts.append(('```css\n' + '\n'.join(h) + '```').replace('    !', '!'))

    return texts