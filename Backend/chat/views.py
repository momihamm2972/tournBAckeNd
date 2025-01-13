from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from rest_framework.views import APIView
from .serializer import mohaSerializer, ChatsSerializer, MessageSerializer,GlobalFriendSerializer,InviteFriendSerializer
from .models import Message,Invitations,Tournament
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from user_management.models import User,Match
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inviteFriend(request):
    serializer = GlobalFriendSerializer(data=request.data)
    jwt_user = request.user.id
    if (serializer.is_valid()):
        user1 = serializer.validated_data.get('user1')
        _type = serializer.validated_data.get('type')
        if jwt_user == user1:
            return Response("Detail: Cant Invite it self", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        o = Invitations.objects.get(Q(user1=user1,user2=jwt_user) | Q(user1=jwt_user,user2=user1))
        #q = user1 <---- mn 3end sma3il
            # return Response("cant invite the player doesnt existe", status=status.HTTP_400_BAD_REQUEST)
    except:
        mydata = {
            "user1": jwt_user,
            "user2": user1,
            "type": _type
        }
        newRecord= InviteFriendSerializer(data=mydata)
        if (newRecord.is_valid()):
            newRecord.save()
            return Response("Invited player successfuly", status=status.HTTP_201_CREATED)
    return Response("invitation already exist", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acceptFriend(request):
    serializer = GlobalFriendSerializer(data=request.data)
    if (serializer.is_valid()):
        validated_data = serializer.validated_data
        user: User = request.user
        user1 = user.id
        user2 = validated_data.get('user1')
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if (user1 == user2):
        return Response("Detail: Cant block", status=status.HTTP_400_BAD_REQUEST)
    try:
        query = Invitations.objects.get(user2=user1,user1=user2,status="pending")
    except:
        return Response("Detail: Invitation not found", status=status.HTTP_404_NOT_FOUND)
    query.status="accepted"
    if query.type == "game":
        query.type = "join"
    query.save()
    if (query.type == "game"):
            return Response(query.friendship_id, status=status.HTTP_200_OK)
    return Response("detail: Invitation accepted successfuly", status=status.HTTP_200_OK)        
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def declineFriend(request):
    serializer = GlobalFriendSerializer(data=request.data)
    if (serializer.is_valid()):
        validated_data = serializer.validated_data
        user: User = request.user
        user1 = user.id
        user2 = validated_data.get('user1')
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if (user1 == user2):
        return Response("Detail: Cant Decline ", status=status.HTTP_400_BAD_REQUEST)

    try:
        query = Invitations.objects.get(user2=user1,user1=user2,status="pending")
        query.delete()
    except:
        return Response("Detail: Invitation Not found", status=status.HTTP_400_BAD_REQUEST)

    return Response("Detail: Declined successfully",status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def blockFriend(request):
    serializer = GlobalFriendSerializer(data=request.data)
    if (serializer.is_valid()):
        validated_data = serializer.validated_data
        user: User = request.user
        user1 = user.id
        user2 = validated_data.get('user2')
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if (user1 == user2):
        return Response("Detail: Cant block", status=status.HTTP_400_BAD_REQUEST)

    try:
        query = Invitations.objects.get((Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)) & Q(status='accepted'))
        query.status="blocked"
        query.save()
    except:
        return Response("Detail: Cant block", status=status.HTTP_400_BAD_REQUEST)
    return Response("Detail: Blocked successfully", status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deblockFriend(request):
    serializer = GlobalFriendSerializer(data=request.data)
    if (serializer.is_valid()):
        validated_data = serializer.validated_data
        user: User = request.user
        user1 = user.id
        user2 = validated_data.get('user2')
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if (user1 == user2):
        return Response("Detail: Cant Deblock", status=status.HTTP_400_BAD_REQUEST)
    try:
        query = Invitations.objects.get((Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)) & Q(status='blocked'))
        query.status="accepted"
        query.save()
    except:
        return Response("Detail: Cant Deblock", status=status.HTTP_400_BAD_REQUEST)
    return Response("Detail: Deblocked successfully", status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getChats(request):
    user: User = request.user
    user_id = user.id
    chats: Invitations = Invitations.objects.filter((Q(user1=user_id) | Q(user2=user_id)) & Q(status="accepted") & Q(type="friend"))
    serializer = ChatsSerializer(chats, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMessages(request, chat=None):
    user: User = request.user
    user_id = user.id
    valid = Invitations.objects.filter(Q(friendship_id=chat) & (Q(user1=user_id) | Q(user2=user_id)))
    if not valid.exists():
        return Response({"error": "Not authorized to see this chat content"}, status=status.HTTP_401_UNAUTHORIZED)
    Messages: Message = Message.objects.filter(chat_id=chat)
    serializer = MessageSerializer(Messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getNotifications(request):
    user: User = request.user
    user_id = user.id
    notifs = Invitations.objects.filter(Q(user2=user_id) & (Q(status="pending") | Q(type="join")))
    serializer = GlobalFriendSerializer(notifs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK) 


def msg(user1, user2, mesg_text):
    print(f"User1: {user1}, User2: {user2}") 
    try:
        invitation_instance = Invitations.objects.get(
            (Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)),
            status="accepted",
            type="friend"
        )
        print(f"Invitation found: {invitation_instance.friendship_id}")  
        message = Message(
            chat_id=invitation_instance,
            sender_id=user1, 
            msg=mesg_text, 
        )
        message.save()
        print("Message sent successully")
    except Invitations.DoesNotExist:
        print("No invitation matches the criteria.")
    except Invitations.MultipleObjectsReturned:
        print("Multiple invitations match the criteria. Please refine your query.") 


def sendmsg(mainUser, userid1, userid2, userid3):
    tournamentUsersId = [mainUser, userid1, userid2, userid3]
    invitID = []
    print(mainUser) 
    for i in range(0, len(tournamentUsersId), 2):
        if i + 1 < len(tournamentUsersId):
            recdata = {
                'user1': tournamentUsersId[i],
                'user2': tournamentUsersId[i + 1],
                'status': 'accepted',  # Matches TypeClass
                'type': 'join'        # Matches InvitationType   
            }
            print(recdata)
            print("\n\n\n")
        serializer = mohaSerializer(data=recdata) 
        if serializer.is_valid():
            print("valid") 
            serializer.save()
            print (tournamentUsersId[i+1]) 
            msg(mainUser , tournamentUsersId[i+1], "You have been invited to a tournament , join now")  
        else:
            print(serializer.errors)   
    msg(mainUser , tournamentUsersId[2], "khouna doz t9sser , daba nikek")
    # return mainUser





def init_tornament(mainUser, userid1, userid2, userid3):
    tornament = Tournament()
    tornament.tournamentID = mainUser
    tornament.tormanemnt_name = f"{mainUser}"
    tornament.available_players = 4
    tornament.position1 = mainUser
    tornament.position2 = userid1
    tornament.position3 = userid2
    tornament.position4 = userid3
    tornament.position5 = None
    tornament.position6 = None
    tornament.position7 = None
    tornament.save() 
    return tornament 

class CreateTournament(APIView):

    def post(self, request):
        try:
            # tournamentOwnerid = request.user.id
            data = json.loads(request.body.decode("utf-8"))
            self.userid1 = data.get('userid1')
            self.userid2 = data.get('userid2')
            self.userid3 = data.get('userid3') 
            # self.mainUser = request.user.id
            self.mainUser = 1337
            self.tournamentUsersId = [self.userid1, self.userid2, self.userid3]
            print (self.mainUser)
            if (not self.userid1 or not self.userid2 or not self.userid3):
                return Response({'message': 'some userids are missing'}) #response as json
            for self.userid in self.tournamentUsersId:
                recordData = {
                    'user1': self.mainUser,
                    'user2': self.userid,
                    'type': 'tournament'
                }
                newRecord = InviteFriendSerializer(data=recordData)
                if (newRecord.is_valid()):
                    newRecord.save()
                else:
                    return Response("invitation failed", status=status.HTTP_400_BAD_REQUEST)
            
            init_tornament(mainUser=self.mainUser, userid1=self.userid1, userid2=self.userid2, userid3=self.userid3)
            sendmsg(mainUser=self.mainUser, userid1=self.userid1, userid2=self.userid2, userid3=self.userid3)
            return Response("Invited players successfuly", status=status.HTTP_201_CREATED)
            return Response({'message': 'Success'})
        except json.JSONDecodeError:
            return Response({'message': 'Error JSON'})



class NextRound(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            self.winner = data.get('winner')
            self.loser = data.get('loser')
            self.score = data.get('score')
            print(self.winner)
            print(self.loser)
            print(self.score)
            
            # Try to get the match instance
            match_instance = Match.objects.get(winner=self.winner)
            print("**********")
            print(match_instance.winner)
            print("**********")
            print(match_instance.loser)

            try:
                invitation = Invitations.objects.get(Q(user2=self.winner) & Q(type="tournament") & Q(status="accepted"))
            except Exception as e:
                print(e)
            self.mainUser = invitation.user1
            print(self.mainUser)
            tornament_instance = Tournament.objects.get(tournamentID=self.mainUser)
            print(self.winner, type(self.winner))
            print(tornament_instance.position5)
            # tornament_instance.position5 = self.winner
            # tournament_instance.save()
            # print(tornament_instance.position5)
            
            return Response({'message': 'Match added successfully'})
        
        except json.JSONDecodeError:
            return Response({'message': 'Error: Invalid JSON format'}, status=400)
        
        except Match.DoesNotExist:
            return Response({'message': f'Error: Match with winner "{self.winner}" does not exist'}, status=404)
        
        except Exception as e:
            # General exception handling for unexpected errors
            return Response({'message': f'Error: {str(e)}'}, status=500)  