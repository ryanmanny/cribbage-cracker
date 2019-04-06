"""
You may notice a general sense of hackiness throughout the game logic.
The intent of this project is to create a good interface to a Cribbage AI that
could be hooked into any Cribbage game. Because of this, this cribbage game
will not be very fun
"""

import random

from card import CribbageDeck, CribbageHand, CribbagePeggingPile


class CribbagePlayer:
    def __init__(self):
        self._game = None

        self._hand = None
        self._pegging_hand = None
        self._points = 0

    def throw_away_cards(self):
        raise NotImplementedError

    def put_down_pegging_card(self):
        raise NotImplementedError

    def print_hand(self):
        print(f"{self.hand!s}")

    @property
    def minimum_card(self):
        """
        Used to check if a player must say GO
        """
        return min(card.value for card in self.hand)

    @property
    def hand(self):
        return self._hand

    @hand.setter
    def hand(self, new_hand):
        """
        Sets both hand variables at the same time, since they are both
        handled independently (this is a hack!)
        """
        self._hand = CribbageHand(new_hand)
        self._pegging_hand = CribbageHand(new_hand)

    @property
    def pegging_hand(self):
        """
        Set using self.hand
        """
        return self._pegging_hand

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        """
        A hacky event handler. Why does the game ask the player if he won?
        """
        self._points = value
        if self._points > 120:
            self._game.win_handler(self)


class RoboCribbagePlayer(CribbagePlayer):
    def throw_away_cards(self):
        raise NotImplementedError

    def put_down_pegging_card(self):
        raise NotImplementedError


class CribbageGame:
    def __init__(self, players):
        if len(players) != 2:
            raise NotImplementedError("Only two players allowed")
        self._players = players
        for player in self._players:
            player._game = self  # Used so AI can query things it needs to

        self._dealer = random.choice(self._players)
        self._crib = CribbageHand()

        self._deck = CribbageDeck()
        self._pegging_pile = CribbagePeggingPile()
        self._cut_card = None

    def win_handler(self, player):
        assert player.points > 120, ValueError("You little scumbag")
        self.game_over(player)

    def game_over(self, player):
        raise NotImplementedError

    def _deal(self):
        for player in self._players:
            player.hand = self._deck.deal(6)

    def _cut(self):
        """
        Automatically cuts, since there is no strategy worth exploring there
        """
        cut_card = self._deck.draw()
        if cut_card.rank == 'Jack':
            self._dealer.points += 2

    def _make_players_throw_away(self):
        """
        Asks players which cards to throw away
        """
        for player in self._players:
            player.throw_away_cards()

    def _make_players_peg(self):
        """
        Performs the pegging process, asking users for input when necessary
        """
        go = False
        last_player = None

        while not all(player.hand.is_empty for player in self._players):
            for player in self._players:
                if go:  # This player plays until she can't go either
                    player.points += 1  # One point for Go
                    while True:
                        go = player.put_down_pegging_card(self._pegging_pile)
                        if go:
                            self._pegging_pile.reset()  # Neither player can play
                            break
                        last_player = player
                elif not player.hand.is_empty:
                    go = player.put_down_pegging_card(self._pegging_pile)
                    last_player = player

        last_player.points += 1  # One for last card
        self._pegging_pile.reset()

    def _count_players_hands(self):
        """
        Abstracts the counting away from the player, it's not very important
        Automatically adds points in the hand to score
        """
        for player in self._players:
            player.points += player.hand.count(self._cut_card)

    def _count_crib(self):
        self._dealer.points += self._crib.count(self._cut_card)

    def turn(self):
        """
        Does all logic necessary for a turn of Cribbage to take place
        """
        self._deck.shuffle()

        self._deal()
        self._make_players_throw_away()

        self._cut()
        self._make_players_peg()

        self._count_players_hands()
        self._count_crib()
