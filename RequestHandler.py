import re
import traceback

from ErrorMailer import SendErrorMail
from CommentBuilder import buildRequestComment
from CommentBuilder import getSignature

class RequestHandler(object):
    # Normal - e.g. {Blue-Eyes White Dragon}
    normalRequestQuery = re.compile(r"(?<=(?<!\{)\{)([^{}]*)(?=\}(?!\}))")
    # Expanded - e.g. {{Blue-Eyes White Dragon}}
    expandedRequestQuery = re.compile(r"\{{2}([^}]*)\}{2}")

    
    def __init__(self):
        pass

    def getNormalRequests(self, comment):
        return self.normalRequestQuery.findall(comment)

    def getExpandedRequests(self, comment):
        return self.expandedRequestQuery.findall(comment)
        
    def buildResponse(self, comment):
        try:
            reply = ''
            normalRequests = self.getNormalRequests(comment)
            expandedRequests = self.getExpandedRequests(comment)

            #If there are 10 or more expanded requests, turn them all into normal requests
            #Reddit has a 10k character limit
            if (len(normalRequests) + len(expandedRequests)) >= 8:
                normalRequests.extend(expandedRequests)
                expandedRequests = []

            for card in normalRequests:
                requestComment = buildRequestComment(card, False)
                if requestComment:
                    reply += requestComment + '\n\n---\n\n'

            for card in expandedRequests:
                requestComment = buildRequestComment(card, True)
                if requestComment:
                    reply += requestComment + '\n\n---\n\n'

            if reply:
                reply += getSignature()
                return reply
            else:
                return None
        except Exception as e:
            SendErrorMail(e, traceback.format_exc())
