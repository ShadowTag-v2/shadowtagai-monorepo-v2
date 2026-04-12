"""
Tests for Glicko-2 rating system
"""

import pytest

from shadowtagai.core.glicko import (
    DEFAULT_RATING,
    DEFAULT_RD,
    DEFAULT_VOLATILITY,
    Glicko2Player,
    Match,
    compare_players,
)


class TestGlicko2Player:
    """Test Glicko-2 player implementation"""

    def test_initialization_defaults(self):
        """Test default player initialization"""
        player = Glicko2Player()

        assert player.get_rating() == DEFAULT_RATING
        assert player.get_rd() == DEFAULT_RD
        assert player.get_vol() == DEFAULT_VOLATILITY

    def test_initialization_custom(self):
        """Test custom player initialization"""
        player = Glicko2Player(rating=1600, rd=100, vol=0.05)

        assert abs(player.get_rating() - 1600) < 0.1
        assert abs(player.get_rd() - 100) < 0.1
        assert abs(player.get_vol() - 0.05) < 0.001

    def test_single_match_win(self):
        """Test rating update after winning"""
        player = Glicko2Player(rating=1500, rd=200, vol=0.06)
        initial_rating = player.get_rating()

        matches = [Match(opponent_rating=1400, opponent_rd=30, outcome=1.0)]

        player.update(matches)

        # Rating should increase after win
        assert player.get_rating() > initial_rating
        # RD should decrease (more certain)
        assert player.get_rd() < 200

    def test_single_match_loss(self):
        """Test rating update after losing"""
        player = Glicko2Player(rating=1500, rd=200, vol=0.06)
        initial_rating = player.get_rating()

        matches = [Match(opponent_rating=1400, opponent_rd=30, outcome=0.0)]

        player.update(matches)

        # Rating should decrease after loss
        assert player.get_rating() < initial_rating
        # RD should decrease (more certain)
        assert player.get_rd() < 200

    def test_multiple_matches(self):
        """Test rating update after multiple matches"""
        player = Glicko2Player(rating=1500, rd=200, vol=0.06)

        matches = [
            Match(opponent_rating=1400, opponent_rd=30, outcome=1.0),  # Win
            Match(opponent_rating=1550, opponent_rd=100, outcome=0.0),  # Loss
            Match(opponent_rating=1700, opponent_rd=300, outcome=0.0),  # Loss
        ]

        player.update(matches)

        # 1 win, 2 losses should decrease rating
        assert player.get_rating() < 1500
        # RD should decrease after games
        assert player.get_rd() < 200

    def test_no_matches_increases_rd(self):
        """Test that inactivity increases rating deviation"""
        player = Glicko2Player(rating=1500, rd=100, vol=0.06)
        initial_rd = player.get_rd()

        # Update with no matches (inactivity)
        player.update([])

        # RD should increase
        assert player.get_rd() > initial_rd
        # Rating should stay same
        assert player.get_rating() == 1500

    def test_decay_rating(self):
        """Test rating decay from inactivity"""
        player = Glicko2Player(rating=1500, rd=100, vol=0.06)
        initial_rd = player.get_rd()

        # Decay for 3 periods
        player.decay_rating(periods=3)

        # RD should increase significantly
        assert player.get_rd() > initial_rd
        # Rating should stay same
        assert player.get_rating() == 1500

    def test_g_function(self):
        """Test Glicko-2 g function"""
        player = Glicko2Player()

        # g(0) should be close to 1
        assert abs(player._g(0) - 1.0) < 0.01

        # g increases as phi decreases (more certain opponents)
        assert player._g(0.1) > player._g(0.5)
        assert player._g(0.5) > player._g(1.0)

    def test_E_function(self):
        """Test expected outcome function"""
        player = Glicko2Player()

        # Equal players: expected score = 0.5
        E_equal = player._E(0, 0, 0.1)
        assert abs(E_equal - 0.5) < 0.01

        # Higher rated player: expected score > 0.5
        E_higher = player._E(0.5, 0, 0.1)
        assert E_higher > 0.5

        # Lower rated player: expected score < 0.5
        E_lower = player._E(-0.5, 0, 0.1)
        assert E_lower < 0.5


class TestComparePlayers:
    """Test player comparison function"""

    def test_equal_players(self):
        """Test comparison of equal players"""
        player1 = Glicko2Player(rating=1500, rd=100, vol=0.06)
        player2 = Glicko2Player(rating=1500, rd=100, vol=0.06)

        comparison = compare_players(player1, player2)

        # Expected scores should be close to 0.5
        assert abs(comparison["expected_score_player1"] - 0.5) < 0.05
        assert abs(comparison["expected_score_player2"] - 0.5) < 0.05
        assert comparison["rating_difference"] == 0

    def test_unequal_players(self):
        """Test comparison of unequal players"""
        player1 = Glicko2Player(rating=1600, rd=100, vol=0.06)
        player2 = Glicko2Player(rating=1400, rd=100, vol=0.06)

        comparison = compare_players(player1, player2)

        # Higher rated player should have higher expected score
        assert comparison["expected_score_player1"] > 0.5
        assert comparison["expected_score_player2"] < 0.5
        assert comparison["rating_difference"] == 200

    def test_confidence(self):
        """Test confidence calculation"""
        # Low RD = high confidence
        player1 = Glicko2Player(rating=1500, rd=50, vol=0.06)
        player2 = Glicko2Player(rating=1500, rd=50, vol=0.06)
        comparison1 = compare_players(player1, player2)

        # High RD = low confidence
        player3 = Glicko2Player(rating=1500, rd=300, vol=0.06)
        player4 = Glicko2Player(rating=1500, rd=300, vol=0.06)
        comparison2 = compare_players(player3, player4)

        # Lower RD should give higher confidence
        assert comparison1["confidence"] > comparison2["confidence"]


class TestGlicko2Scenarios:
    """Test realistic Glicko-2 scenarios"""

    def test_new_player_vs_experienced(self):
        """Test new player (high RD) vs experienced (low RD)"""
        new_player = Glicko2Player(rating=1500, rd=350, vol=0.06)
        experienced = Glicko2Player(rating=1500, rd=50, vol=0.06)

        # New player wins
        new_player.update([Match(opponent_rating=1500, opponent_rd=50, outcome=1.0)])

        # Experienced loses
        experienced.update([Match(opponent_rating=1500, opponent_rd=350, outcome=0.0)])

        # New player's rating should change more (higher RD)
        new_rating_change = abs(new_player.get_rating() - 1500)
        exp_rating_change = abs(experienced.get_rating() - 1500)

        assert new_rating_change > exp_rating_change

    def test_consistency_vs_volatility(self):
        """Test consistent performer vs volatile performer"""
        consistent = Glicko2Player(rating=1500, rd=100, vol=0.03)
        volatile = Glicko2Player(rating=1500, rd=100, vol=0.09)

        # Both have same results
        matches = [
            Match(opponent_rating=1400, opponent_rd=50, outcome=1.0),
            Match(opponent_rating=1600, opponent_rd=50, outcome=0.0),
        ]

        consistent.update(matches)
        volatile.update(matches)

        # Volatile player should maintain higher volatility
        assert volatile.get_vol() > consistent.get_vol()

    def test_winning_streak(self):
        """Test effect of winning streak"""
        player = Glicko2Player(rating=1500, rd=100, vol=0.06)

        # Win 5 games in a row against equal opponents
        for _ in range(5):
            player.update([Match(opponent_rating=1500, opponent_rd=100, outcome=1.0)])

        # Rating should increase significantly
        assert player.get_rating() > 1600
        # RD should decrease (more certainty)
        assert player.get_rd() < 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
