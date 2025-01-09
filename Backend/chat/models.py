from django.db import models

class Invitations(models.Model):
    
    class TypeClass(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        BLOCKED = "blocked"
    
    class InvitationType(models.TextChoices):
        GAME = "game"
        FRIEND = "friend"
        TOURNAMENT = "tournament"
        JOIN = "join"
    
    friendship_id = models.AutoField(primary_key=True)
    user1 = models.IntegerField()
    user2 = models.IntegerField()
    status = models.CharField(max_length=8, choices=TypeClass.choices, default=TypeClass.PENDING)
    type = models.CharField(max_length=10, choices=InvitationType.choices)
    
    
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['user1', 'user2'], name='unique_user_pair')
    #     ]


class Message(models.Model):
    chat_id = models.ForeignKey(Invitations, on_delete=models.CASCADE, related_name="messages")
    sender_id = models.IntegerField()
    msg = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def formatted_sent_at(self):
        return self.sent_at.strftime('%Y-%m-%d %H:%M:%S')















class Tournament(models.Model):
    tournamentID = models.PositiveIntegerField(primary_key=True)  # Unique ID for the tournament
    tormanemnt_name = models.CharField(max_length=100)  # Name of the tournament
    available_players = models.IntegerField(default=0)  # Number of players available
    # Positions for users in the tournament
    position1 = models.PositiveIntegerField(null=True, blank=True)
    position2 = models.PositiveIntegerField(null=True, blank=True)
    position3 = models.PositiveIntegerField(null=True, blank=True)
    position4 = models.PositiveIntegerField(null=True, blank=True)
    position5 = models.PositiveIntegerField(null=True, blank=True)
    position6 = models.PositiveIntegerField(null=True, blank=True)
    position7 = models.PositiveIntegerField(null=True, blank=True)


    def __str__(self):
        return f"Tournament {self.tournamentID}: name of tournament is {self.tormanemnt_name},  {self.available_players} players available"
    def readytoplay(self):
        if self.available_players == 4:
            return True
        return False
    # def makeID(self):
    # @classmethod
    # def make_tournament(cls, main_user, user_ids):
    #     if not user_ids or len(user_ids) > 4:
    #         return {"message": "User IDs must be between 1 and 4", "status": 400}

    #     try:
    #         # Create the tournament and assign positions
    #         tournament_data = {
    #             'tournamentID': main_user,  # Set the tournament ID to be the creator's ID
    #             'available_players': len(user_ids),
    #         }
    #         # for i, user_id in enumerate(user_ids):
    #         #     tournament_data[f'position{i+1}'] = user_id

    #         # tournament = cls.objects.create(**tournament_data)
    #         # print(f"Tournament {tournament} created successfully.")
    #         # return {"message": "Tournament created successfully", "status": 201}

    #     except Exception as e:
    #         return {"message": f"Error: {str(e)}", "status": 500}


#posion ghadi 
#momihamm 



# fun 1
# {
#     fun2
#     fun3

# }