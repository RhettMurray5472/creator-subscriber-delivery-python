import unittest

from src.creator_delivery import Post, delivery_decision


class DeliveryDecisionTest(unittest.TestCase):
    def test_only_published_posts_are_ready_for_subscribers(self):
        published = Post("Published guide", "retrieval notes", "published")
        draft = Post("Draft guide", "retrieval notes", "draft")

        self.assertTrue(delivery_decision(published)["deliver"])
        self.assertEqual(delivery_decision(published)["status"], "ready")
        self.assertFalse(delivery_decision(draft)["deliver"])
        self.assertEqual(delivery_decision(draft)["status"], "processing")


if __name__ == "__main__":
    unittest.main()
