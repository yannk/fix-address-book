import gdata
import gdata.contacts
import gdata.contacts.client
import atom
import distance
import sys


print "use at your own risk"
sys.exit(0)

#atom.MEMBER_STRING_ENCODING = "unicode"

email = 'you@gmail.com'
password = "apppassword"
source = "fix-address-book"
client = gdata.contacts.client.ContactsClient(source=source)
client.ClientLogin(email, password, source)

def delete_extra_emails(id, keep, full_name, entry):
    return
    entry.email = []
    for k in keep:
        entry.email.append(gdata.data.Email(address=k, rel=gdata.data.HOME_REL))
    #print "for id: %s, keep=%s, full_name=%s, d=%s" % (id, keep, full_name, ",".join([e.address for e in entry.email]))
    client.Update(entry)

def delete_empty(id, entry):
    if len(entry.email) > 1:
        # if there are more than on email, but no name, it's probably junk
        emails = ", ".join([e.address for e in entry.email])
        #print "delete", id, emails
        client.Delete(entry)


q = gdata.contacts.client.ContactsQuery()
q.max_results = 10000
feed = client.GetContacts(q=q)
for i, entry in enumerate(feed.entry):
    id = entry.id.text
    id = id.split('/')[-1]

    if not entry.name:
        delete_empty(id, entry)
        continue

    if len(entry.email) < 3:
        # most likely not an email leakage
        continue

    full_name = entry.name.full_name or entry.name.family_name or entry.name.given_name
    if full_name is not None:
        full_name = full_name.text

    if not full_name:
        print "empty full name"
        continue

    l_full_name = full_name.lower()
    min_distance = 0.5
    keep_emails = []
    for email in entry.email:
        username = email.address.split('@')[0]
        #d = distance.nlevenshtein(username.lower(), l_full_name)
        #d2 = distance.jaccard(username.lower(), l_full_name)
        d3 = distance.sorensen(username.lower(), l_full_name)
        if d3 <= min_distance:
            keep_emails.append(email.address)

    if len(keep_emails) != len(entry.email):
        delete_extra_emails(id, keep_emails, full_name, entry)
