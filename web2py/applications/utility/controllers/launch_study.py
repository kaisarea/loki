import string
import random

def id_generator(size=30, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

# launch_study(1000, 'genova', 'genova live 1', 'One monday late, here goes launch.')

# now we wanna select all unlaunched hits and assign them random hitids


rows = db((db.hits.hitid == None) & (db.hits.study == 8) & (db.hits.status == 'unlaunched')).select()
print(db((db.hits.hitid == None) & (db.hits.study == 8) & (db.hits.status == 'unlaunched')).count())
xml_stuff = ''

for hit in rows:
	hit_id = id_generator()
	db(db.hits.id == hit.id).update(hitid = hit_id)
	db(db.hits.id == hit.id).update(status = 'open')
	print(db(db.hits.id == hit.id).select()[0].hitid)

# sample hit id 2ACHYW2GTP9RIOQ5G2S6CYSONZBSND: 30 

"""<?xml version="1.0" ?>
				<GetHITResponse>
					<OperationRequest>
					<RequestId>0139f6c5-bdba-4efd-abb7-47f85aa4aef0</RequestId>
					</OperationRequest>
					<HIT>
					<Request>
					<IsValid>True</IsValid>
					</Request>
					<HITId>3P888QFVX3U0AM7AHFIRJKGPSDSOQ5</HITId>
					<HITTypeId>2F7PLSP75KLMEDH38Q8QHQVJRSJTZ1</HITTypeId>
					<CreationTime>2014-06-22T20:46:52Z</CreationTime>
					<Title>Clearing House - Different Task Each Day! (Pays Bonus)</Title>
					<Description>We aggregate tasks from many clients.  Tasks and task details change each day.  
						View today's HIT to see it and decide if you like it.
					</Description>
					<Question>&lt;ExternalQuestion xmlns=&quot;http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd&quot;&gt;
  &lt;ExternalURL&gt;https://yuno.us:443/genova?live&lt;/ExternalURL&gt;
  &lt;FrameHeight&gt;650&lt;/FrameHeight&gt;
&lt;/ExternalQuestion&gt;</Question>
<Keywords>CrowdClearinghouse, Clearing House, Clearinghouse, random, bonus</Keywords>
<HITStatus>Assignable</HITStatus>
<MaxAssignments>1</MaxAssignments>
<Reward><Amount>0.00</Amount>
<CurrencyCode>USD</CurrencyCode>
<FormattedPrice>$0.00</FormattedPrice>
</Reward>
<AutoApprovalDelayInSeconds>2592000</AutoApprovalDelayInSeconds>
<Expiration>2014-06-23T20:46:52Z</Expiration>
<AssignmentDurationInSeconds>3600</AssignmentDurationInSeconds>
<RequesterAnnotation>None</RequesterAnnotation>
<QualificationRequirement><QualificationTypeId>00000000000000000071</QualificationTypeId>
<Comparator>EqualTo</Comparator><LocaleValue>
<Country>US</Country></LocaleValue><RequiredToPreview>1</RequiredToPreview></QualificationRequirement>
<HITReviewStatus>NotReviewed</HITReviewStatus></HIT></GetHITResponse>"""