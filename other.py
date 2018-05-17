import re
import constants as C
import datetime


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


def str_keys(dict,keys,pre=''):
    ans=[]
    for key in keys:
        if key in dict:
            ans.append(pre + '[' + key + '] = ' + dict[key])
    return '\n'.join(ans) if ans else []


def mess_plus(message):
    if message.attachments:
        attachments = []
        for att in message.attachments:
            attachments.append('\t\t' + att['url'])
        print('\n'.join(attachments))
    if message.embeds: # TODO Check and debug this block
        embeds = []
        i = 1
        for emb in message.embeds:
            embed = ['\tEmb_'+str(i)+':']
            embed += [str_keys(emb, ['title', 'url', 'description'], '\t\t')]
            if 'author' in emb:
                embed += ['\t\t[author]:']
                embed += [str_keys(emb['author'], ['name', 'icon_url'], '\t\t\t')]

            if 'fields' in emb:
                j = 1
                for field in emb['fields']:
                    embed += ['\t\t[field_' + str(j) + ']:']
                    embed += [str_keys(field, ['name', 'value'], '\t\t\t')]
                    j += 1

            if 'footer' in emb:
                embed += ['\t\t[footer]:']
                embed += [str_keys(emb['footer'], ['icon_url', 'text'], '\t\t\t')]

            i += 1
            embeds.append('\n'.join(embed))

        print('\n'.join(embeds))


def t2s(timedata=None, frm="%H:%M:%S"):
    timedata = timedata or datetime.datetime.utcnow()
    timedata = timedata.replace(tzinfo=timedata.tzinfo or datetime.timezone.utc)
    return timedata.astimezone(datetime.timezone(datetime.timedelta(hours=3))).strftime(frm)


def get_user(i): # i must be id, server nickname, true nickname or full nickname (SomeName#1234)
    return C.server.get_member(i) or C.server.get_member_named(i)

#fl = discord.utils.get(cl.get_all_channels(),name='flood')

