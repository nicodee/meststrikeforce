from models import User, Message, Contribution, Program, Company
from time import gmtime, strftime
import mandrill
import exceptions
import access
import mailContent
KEY = access.mandrill_key 


#sending an outbound mail. From entrepreneur to mentor or job applicant
def outBoundMail(message):

    from_email = message.get("sender_email")
    from_name  = message.get("sender_name")
    to_email   = message.get("receiver_email")
    to_name    = message.get("receiver_name")
    subject    = message.get("subject")
    html       = message.get("content")
    reply_to   = message.get("reply_to")
    tags       = "Outbound Mail"

    merge      = False
    variables  = None 
    return sendOutboundMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables, merge)
    
    
def sendOutboundMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables, merge):
    try:
        mandrill_client = mandrill.Mandrill(KEY)
        message = {'auto_html': True,
         'auto_text': True,
         'from_email': from_email,
         'from_name': from_name,
         'global_merge_vars': [{'content': 'merge1 content', 'name': 'merge1'}],
         'headers': {'Reply-To': reply_to},
         'html': html,
         'important': True,
         'inline_css': True,
         'merge': merge,
         'merge_vars': [{'rcpt': to_email, 'vars': variables}],
         'metadata': {'website': 'www.meststrikeforce.appspot.com'},
         'preserve_recipients': None,
         'recipient_metadata': [{'rcpt': to_email,
                                 'values': {'rcpt_name': to_name}
                                 }],
         'signing_domain': None,
         'subject': subject,
         'tags': [tags],
         'text': html,
         'to': [{'email': to_email}],
         'track_clicks': True,
         'track_opens': True,
         'tracking_domain': None,
         'url_strip_qs': None}
        result = mandrill_client.messages.send(message=message, async=False, ip_pool='Main Pool')
        print result[0].get("_id")
        return result


    except mandrill.Error, e: 
        return 'A mandrill error occurred: %s - %s' % (e.__class__, e)
#outbound mail ends here

def getAdminDetails():
    recipient    = {}

    recipient['name']  = "Administration" 
    recipient['email'] = "incubator@meltwater.org"
    recipient['alias'] = "admin@meststrikeforce.appspotmail.com"

    return recipient

user_role = {"Entrepreneur": "an Entrepreneur", "Mentor": "a Mentor", "Job Applicant": "a Freelancer"}

def requestMail(user):
    new_user_name    = user.first_name + " " + user.last_name
    new_user_role    = user_role.get(user.user_profile)

    from_email       = "admin@meststrikeforce.appspotmail.com" 
    from_name        = "MEST Strike Force"

    recipient        = getAdminDetails();

    to_email         = recipient.get("email")
    to_name          = recipient.get("name")

    subject          = "Request For Confirmation"
    html             = mailContent.request
    reply_to         = recipient.get("alias")
    tags             = "Request For Confirmation"

    confirmation_url = access.admin_url

    variables        = [{'name': 'username', 'content': new_user_name}, 
                        {'name': 'role', 'content': new_user_role }, 
                        {'name':'confirmation_url', 'content': confirmation_url}]

    print sendRequestMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables)


def requestMentorMail(user):
    def get_job(user):
        mentor = user
        # try: 
        if mentor.positions.count() > 0: 
            for position in mentor.positions.filter('is_current =', True): 
                return "%s at %s" %(position.title, position.company)
        else:
            for school in mentor.educations.order('-end_date').fetch(limit=1): 
                return "Student at %s" %(school.school_name)
        # except:
        #     return None
    new_user_name    = user.first_name + " " + user.last_name
    new_user_role    = user_role.get(user.user_profile)

    from_email       = "admin@meststrikeforce.appspotmail.com" 
    from_name        = "MEST Strike Force"

    recipient        = getAdminDetails();

    to_email         = recipient.get("email")
    to_name          = recipient.get("name")

    subject          = "New MEST Strike Force member!"
    html             = mailContent.request_mentor
    reply_to         = recipient.get("alias")
    tags             = "Request For Mentor Confirmation"

    confirmation_url = access.admin_url

    variables        = [{'name': 'username', 'content': new_user_name}, 
                        {'name': 'role', 'content': new_user_role }, 
                        {'name':'confirmation_url', 'content': confirmation_url},
                        {'name': 'location', 'content': user.location},
                        {'name': 'job', 'content': get_job(user)}]

    print sendRequestMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables)


def sendRequestMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables):
    try:
        mandrill_client = mandrill.Mandrill(KEY)
        message = {'auto_html': True,
         'auto_text': True,
         'from_email': from_email,
         'from_name': from_name,
         'global_merge_vars': [{'content': 'merge1 content', 'name': 'merge1'}],
         'headers': {'Reply-To': reply_to},
         'html': html,
         'important': True,
         'inline_css': True,
         'merge': True,
         'merge_vars': [{'rcpt': to_email, 'vars': variables}],
         'metadata': {'website': 'www.meststrikeforce.appspot.com'},
         'preserve_recipients': None,
         'recipient_metadata': [{'rcpt': to_email,
                                 'values': {'user_id': 123456}}],
         'signing_domain': None,
         'subject': subject,
         'tags': [tags],
         'text': "text",
         'to': [{'email': to_email}],
         'track_clicks': True,
         'track_opens': True,
         'tracking_domain': None,
         'url_strip_qs': None}
        result = mandrill_client.messages.send(message=message, async=False, ip_pool='Main Pool')
        return result


    except mandrill.Error, e: 
        return 'A mandrill error occurred: %s - %s' % (e.__class__, e)


def composeNewMail(message):
    user = message.get('sender')  
    notify = message.get('notification_email')
    result = False
    try:
        result = outBoundMail(message)
    except:
        return False      
    if result != False:
        try:
            msg = Message.create(message)
            user.notify_mail = notify
            user.put()
            # print user.notify_mail
            return result
        except:
            return False
    else:
        return False
 

def notifyEntrepreneur(message):
    user       = message.get("receiver")
    from_email = message.get("sender_email")
    from_name  = message.get("sender_name")
    to_email   = user.notify_mail
    to_name    = message.get("sender_name")
    subject    = "You just received a mail on the MEST Strike Force."
    html       = mailContent.notification_received

    reply_to   = "admin@meststrikeforce.appspotmail.com"
    tags       = "Outbound Mail"

    confirmation_url = access.message_url
    variables  = [  {'name': 'username', 'content': message.get("receiver").first_name + " " +message.get("receiver").last_name},
                    {'name': 'sender_name', 'content': message.get("sender").first_name + " " +message.get("sender").last_name}, 
                    {'name': 'role', 'content'    : message.get("sender").user_profile },
                    {'name':'read_url', 'content': confirmation_url}]
    merge      = False
    return sendOutboundMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables, merge)


def confirmUserMail(user):
    from_email = "admin@meststrikeforce.appspotmail.com"
    from_name  = "MEST Strike Force"
    to_email = user.notify_mail
    to_name  = user.first_name + " " + user.last_name
    subject = "Welcome to the MEST Strike Force!"
    
    confirmation_url = access.signin_url
    
    if user.user_profile == "Mentor":
        html = mailContent.confirm_user_mentor
        variables = [{ 'name': 'username', 'content': to_name},
                {'name': 'server_url', 'content': access.server_url},
                {'name': 'signin_url', 'content': confirmation_url},
                {'name': 'confirmation_url', 'content': confirmation_url}]  

    elif user.user_profile == "Entrepreneur":
        html = mailContent.confirm_user
        variables = [{ 'name': 'username', 'content': to_name},
                    {'name': 'signin_url', 'content': confirmation_url},
                    {'name': 'confirmation_url', 'content': confirmation_url}]


    reply_to = "incubator@meltwater.org"
    tags = "Confirmed User"
    merge = False
    return sendOutboundMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables, merge)


def notificationMail(user):
    from_email = "admin@meststrikeforce.appspotmail.com"
    from_name  = "MEST Strike Force"
    to_email = user.notify_mail
    to_name  = user.first_name + " " + user.last_name
    user_profile = ""
    if user.user_profile == "Mentor":
        user_profile = "a member of"
        subject = "Thank you for joining the MEST Strike Force!"          
    else:
        user_profile = "an Entrepreneur on"        
        subject = "We've Received Your Entrepreneur Application"          
    html = mailContent.signup_template
    variables = [{ 'name': 'username', 'content': to_name},
                {'name': 'userprofile', 'content': user_profile},
                {'name':'firstname', 'content': user.first_name}]
    reply_to = "incubator@meltwater.org"
    tags = "Confirmed User"
    merge = False
    return sendOutboundMail(from_email, from_name, to_email, to_name, subject, html, tags, reply_to, variables, merge)


def sendContributionMails(contribution, mentor):
    result = sendContributionMailAdmin(contribution, mentor)


def sendContributionMailAdmin(contribution, mentor):
    admin       = User.all().filter("user_profile =", "Administrator").get()
    from_email  = "admin@meststrikeforce.appspotmail.com"
    from_name   = "MEST Strike Force"
    to_email    = "admin@meststrikeforce.appspotmail.com"
    to_name     = admin.first_name + " " + admin.last_name    
    mentor_name = mentor.first_name + " " + mentor.last_name
    subject     = "%s has submitted hours for supporting %s" %(mentor_name, contribution.get("company","")) 
    html        = mailContent.newhour
    twitter     = ""
    if mentor.programs[0].twitter_handle != None:
        twitter = "Give %s a high-five via Twitter! Twitter handle: http://twitter.com/%s  <br><br>" %(mentor_name,mentor.programs[0].twitter_handle)
    
    variables   = [
                    {'name':'contributors_full_name', 'content': mentor_name},
                    {'name':'contributed_hours', 'content': contribution.get("hours","")},
                    {'name':'company_name', 'content': contribution.get("company","")},
                    {'name':'twitter', 'content': twitter},
                    {'name':'contributors_first_name', 'content': mentor.first_name},
                    {'name':'description', 'content': contribution.get("description","")}
                ]
    reply_to    = "admin@meststrikeforce.appspotmail.com"
    tags        = "New hour contributed"
    merge       = False
    ceo         = getContributionCEO(contribution)
    try: 
        second =  sendOutboundMail(from_email, from_name, admin.email, to_name, subject, html, tags, reply_to, variables, merge)
        third  =  sendOutboundMail(from_email, from_name, ceo.get("to_email"), ceo.get("to_name"), subject, html, tags, reply_to, variables, merge)
        fourth =  sendBadgeMail(from_email, from_name, contribution, mentor, admin, reply_to, merge, to_name, twitter)
        return True
    except:
        return False


def getContributionCEO(contribution):
    company = Company.all().filter("name =", contribution.get("company")).get()
    ceo = {}
    ceo['to_email'] = company.ceo_email
    ceo['to_name']  = company.ceo_name
    return ceo


def sendBadgeMail(from_email, from_name, contribution, mentor, admin, reply_to, merge, to_name, twitter):
    sendmail = False
    contributed_hours = contribution.get("new_total")

    badge_category = ""
    badge_name = ""

    contributors_first_name = mentor.first_name

    program = Program.all().filter("user = ", mentor).get()

    to_name_mentor = mentor.first_name + " " + mentor.last_name
    subject = "%s just earned a new badge!" %(to_name_mentor)
    mentor_subject ="You've earned a new badge!"
    tags = "New badge earned"

    if contributed_hours >= 250 and program.grand_master == None:
        sendmail = True
        badge_category = "GRAND MASTER"
        badge_name = "Badge250"
        program.scout_master = True
        program.sensei  = True 
        program.captain  = True    
        program.general  = True     
        program.grand_master  = True
        program.put() 

    elif contributed_hours >= 100 and program.general == None:
        sendmail = True
        badge_category = "GENERAL"
        badge_name = "Badge100"
        program.scout_master = True
        program.sensei  = True 
        program.captain  = True    
        program.general  = True
        program.put()

    elif contributed_hours >= 50 and program.captain == None:
        sendmail = True
        badge_category = "CAPTAIN"
        badge_name = "Badge50"
        program.scout_master = True
        program.sensei  = True 
        program.captain  = True
        program.put()
    
    elif contributed_hours >= 25 and program.sensei == None:
        sendmail = True
        badge_name = "Badge25"
        badge_category = "SENSEI"
        program.scout_master = True
        program.sensei  = True
        program.put()
    
    elif contributed_hours >= 10 and program.scout_master == None:
        sendmail = True
        badge_name = "Badge10"
        badge_category = "SCOUT MASTER"
        program.scout_master = True
        program.put()
    
    to_email_mentor = mentor.email
    html_mentor = mailContent.newbadge
    variables_mentor = [
                    {'name':'contributors_first_name', 'content': contributors_first_name},
                    {'name':'contributed_hours', 'content': contributed_hours},
                    {'name': 'server_url', 'content': access.server_url},
                    {'name':'badge_name', 'content': badge_name},
                    {'name':'badge_category', 'content': badge_category}
                ] 
    
    to_email_admin = admin.email
    to_name_admin = to_name
    html_admin = mailContent.newbadgeadmin
    variables_admin = [
                    {'name':'contributors_full_name', 'content': to_name_mentor},
                    {'name':'badge_category', 'content': badge_category},
                    {'name':'contributed_hours', 'content': contributed_hours},
                    {'name': 'server_url', 'content': access.server_url},
                    {'name':'twitter', 'content': twitter},
                    {'name':'contributors_first_name', 'content': contributors_first_name}
                ]
    if  sendmail:
        try:
            mentor_mail  =  sendOutboundMail(from_email, from_name, to_email_mentor, to_name_mentor, mentor_subject, html_mentor, tags, reply_to, variables_mentor, merge) 
            admin_mail   =  sendOutboundMail(from_email, from_name, to_email_admin, to_name_admin, subject, html_admin, tags, reply_to, variables_admin, merge)        
            return True
        except:
            return False

    return True
            


