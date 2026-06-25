"""话题推荐引擎：基于时间/情绪/用户状态推荐对话话题"""
import random
from datetime import datetime


class TopicEngine:
    """基于时间/情绪/用户状态推荐话题"""

    TOPIC_CATEGORIES = {
        "daily_checkin": {
            "name": "每日签到",
            "description": "记录今天的心情",
            "icon": "🌞",
            "prompts": [
                "今天感觉怎么样？用一个词形容一下",
                "今天有什么开心/不开心的事想分享吗？",
            ],
        },
        "emotion_diary": {
            "name": "情绪日记",
            "description": "记录和探索情绪",
            "icon": "📔",
            "prompts": [
                "最近让你印象深刻的一个情绪是什么？",
                "试着描述一下此刻的心情画面",
            ],
        },
        "mindfulness": {
            "name": "正念练习",
            "description": "放松身心",
            "icon": "🧘",
            "prompts": [
                "我们来做一个2分钟的呼吸练习好吗？",
                "试试闭上眼睛，感受此刻身体的状态",
            ],
        },
        "cbt_practice": {
            "name": "思维练习",
            "description": "认知行为练习",
            "icon": "💡",
            "prompts": [
                "最近有没有什么想法让你不舒服？我们来一起分析一下",
                "想尝试挑战一下某个消极想法吗？",
            ],
        },
        "emotion_skills": {
            "name": "情绪管理",
            "description": "学习情绪技巧",
            "icon": "🛡️",
            "prompts": [
                "想学习一个新的情绪管理小技巧吗？",
                "我们来聊聊如何应对压力",
            ],
        },
        "gratitude": {
            "name": "感恩练习",
            "description": "发现生活中的美好",
            "icon": "🌸",
            "prompts": [
                "说出今天3件让你感到感谢的小事",
                "最近有谁对你很好？想对ta说什么？",
            ],
        },
    }

    # 基于时间段的权重配置（早上/下午/晚上）
    _TIME_WEIGHTS = {
        "morning": {
            "daily_checkin": 3,
            "emotion_diary": 1,
            "mindfulness": 1,
            "cbt_practice": 1,
            "emotion_skills": 2,
            "gratitude": 2,
        },
        "afternoon": {
            "daily_checkin": 1,
            "emotion_diary": 2,
            "mindfulness": 2,
            "cbt_practice": 2,
            "emotion_skills": 3,
            "gratitude": 1,
        },
        "evening": {
            "daily_checkin": 1,
            "emotion_diary": 3,
            "mindfulness": 3,
            "cbt_practice": 1,
            "emotion_skills": 1,
            "gratitude": 2,
        },
    }

    # 基于情绪的权重加成
    _EMOTION_WEIGHTS = {
        "sad": {"gratitude": 3, "mindfulness": 2, "emotion_diary": 2},
        "anxious": {"mindfulness": 3, "cbt_practice": 3, "emotion_skills": 2},
        "angry": {"mindfulness": 2, "emotion_skills": 3, "cbt_practice": 2},
        "happy": {"gratitude": 3, "emotion_diary": 2, "daily_checkin": 2},
        "neutral": {"emotion_diary": 2, "emotion_skills": 2, "cbt_practice": 1},
    }

    @staticmethod
    def _get_time_period(hour: int | None = None) -> str:
        if hour is None:
            hour = datetime.now().hour
        if hour < 12:
            return "morning"
        if hour < 18:
            return "afternoon"
        return "evening"

    def get_recommendations(
        self,
        user_id: int | None = None,
        time_of_day: str | None = None,
        recent_emotion: str | None = None,
    ) -> list[dict]:
        """返回 3 个推荐话题（含随机 prompt）"""
        period = time_of_day or self._get_time_period()
        base_weights = dict(self._TIME_WEIGHTS.get(period, self._TIME_WEIGHTS["morning"]))

        # 叠加情绪权重
        if recent_emotion:
            emotion_map = self._EMOTION_WEIGHTS.get(recent_emotion, {})
            for key, bonus in emotion_map.items():
                base_weights[key] = base_weights.get(key, 0) + bonus

        # 加权随机抽样 3 个不重复类别
        categories = list(base_weights.keys())
        weights = [base_weights[c] for c in categories]
        selected_keys: list[str] = []
        for _ in range(min(3, len(categories))):
            if not categories:
                break
            pick = random.choices(categories, weights=weights, k=1)[0]
            idx = categories.index(pick)
            selected_keys.append(pick)
            categories.pop(idx)
            weights.pop(idx)

        # 构建返回结构
        results = []
        for key in selected_keys:
            cat = self.TOPIC_CATEGORIES[key]
            prompt = random.choice(cat["prompts"])
            results.append(
                {
                    "id": key,
                    "name": cat["name"],
                    "description": cat["description"],
                    "icon": cat["icon"],
                    "prompt": prompt,
                }
            )
        return results


# 全局单例
topic_engine = TopicEngine()
