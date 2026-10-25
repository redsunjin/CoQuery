/* Reviewed fixed puzzle data; independent of SQL/provider commands. */
(function (root) {
  "use strict";
  const puzzles = [
  {
    "id": "C1",
    "type": "condition",
    "level": "안내형",
    "title": "두 조건을 모두 만족하기",
    "prompt": "빨강 그리고 원인 카드를 모두 예상해 보세요.",
    "mode": "and",
    "expected": [
      "A"
    ],
    "hint": "A와 B는 모두 빨강이지만 모양은 다릅니다.",
    "explanation": "A만 두 조건을 모두 만족합니다. B는 원이 아니고 C는 빨강이 아닙니다.",
    "rubric": "두 조건을 모두 만족해야 함을 설명하고, B 또는 C가 제외되는 이유를 말한다.",
    "counter": "빨강이기만 한 B를 포함하면 AND 조건에 맞지 않습니다.",
    "version": "0.1.1",
    "data": [
      {
        "id": "A",
        "color": "빨강",
        "shape": "원"
      },
      {
        "id": "B",
        "color": "빨강",
        "shape": "네모"
      },
      {
        "id": "C",
        "color": "파랑",
        "shape": "원"
      },
      {
        "id": "D",
        "color": "파랑",
        "shape": "네모"
      },
      {
        "id": "E",
        "color": "노랑",
        "shape": "세모"
      },
      {
        "id": "F",
        "color": "초록",
        "shape": "별"
      }
    ],
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "C2",
    "type": "condition",
    "level": "독립형",
    "title": "하나 이상이면 남기기",
    "prompt": "빨강 또는 원인 카드를 모두 예상해 보세요. 또는은 하나 이상을 뜻합니다.",
    "mode": "or",
    "expected": [
      "A",
      "B",
      "C"
    ],
    "hint": "두 조건을 모두 만족하는 A도 포함됩니다.",
    "explanation": "A·B·C가 남습니다. B는 빨강, C는 원이며 A는 둘 다 만족합니다.",
    "rubric": "포함적 OR를 설명하고 A가 제외되지 않는 이유를 말한다.",
    "counter": "두 조건을 모두 만족하는 A를 빼는 해석은 이 퍼즐의 OR가 아닙니다.",
    "version": "0.1.1",
    "data": [
      {
        "id": "A",
        "color": "빨강",
        "shape": "원"
      },
      {
        "id": "B",
        "color": "빨강",
        "shape": "네모"
      },
      {
        "id": "C",
        "color": "파랑",
        "shape": "원"
      },
      {
        "id": "D",
        "color": "파랑",
        "shape": "네모"
      },
      {
        "id": "E",
        "color": "노랑",
        "shape": "세모"
      },
      {
        "id": "F",
        "color": "초록",
        "shape": "별"
      }
    ],
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "C3",
    "type": "condition",
    "level": "전이형",
    "title": "10 이상과 10 초과",
    "prompt": "가상 점수 P=9, Q=10, R=11입니다. 기준을 바꿔 두 경우를 모두 예측해 보세요.",
    "mode": "boundary",
    "expected": [
      "Q",
      "R"
    ],
    "hint": "경계값과 같은 Q=10을 먼저 확인해 보세요.",
    "explanation": "10 이상은 Q·R, 10 초과는 R만 포함합니다. 10은 이상에만 포함됩니다.",
    "rubric": "값 10의 포함 여부를 설명하고 두 규칙의 결과 차이를 말한다.",
    "counter": "10 초과에 Q=10을 포함하면 경계 조건에 맞지 않습니다.",
    "version": "0.1.1",
    "data": [
      {
        "id": "P",
        "score": 9
      },
      {
        "id": "Q",
        "score": 10
      },
      {
        "id": "R",
        "score": 11
      }
    ],
    "expectedVariants": {
      "base": [
        "Q",
        "R"
      ],
      "strict": [
        "R"
      ]
    },
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "R1",
    "type": "relation",
    "level": "안내형",
    "title": "한 사람에게 여러 기록",
    "prompt": "회원 ID로 연결하고 대여 기록이 있는 회원만 남깁니다. 결과 행 수를 예상해 보세요.",
    "mode": "inner",
    "expected": 3,
    "hint": "솔의 대여 기록은 책 A와 책 B 두 개입니다.",
    "explanation": "솔–책 A, 솔–책 B, 별–책 C의 3행입니다. 달은 대여가 없습니다.",
    "rubric": "솔이 두 행이 되는 이유와 달이 빠지는 이유를 설명한다.",
    "counter": "회원 수 3명과 결과 3행은 우연히 같습니다. 회원 수로 항상 행 수를 예측할 수 없습니다.",
    "version": "0.1.1",
    "data": {
      "members": [
        {
          "id": "m1",
          "name": "솔"
        },
        {
          "id": "m2",
          "name": "별"
        },
        {
          "id": "m3",
          "name": "달"
        }
      ],
      "loans": [
        {
          "id": "l1",
          "member_id": "m1",
          "book": "책 A"
        },
        {
          "id": "l2",
          "member_id": "m1",
          "book": "책 B"
        },
        {
          "id": "l3",
          "member_id": "m2",
          "book": "책 C"
        }
      ]
    },
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "R2",
    "type": "relation",
    "level": "독립형",
    "title": "기록이 없어도 남기기",
    "prompt": "회원 ID로 연결하되 모든 회원을 남깁니다. 결과 행 수를 예상해 보세요.",
    "mode": "left",
    "expected": 4,
    "hint": "달은 없어지는 대신 대여 없음이라는 행으로 남습니다.",
    "explanation": "기존 3행에 달–대여 없음이 추가되어 4행입니다.",
    "rubric": "연결되지 않은 회원을 남기는 조건과 대여 없음의 의미를 설명한다.",
    "counter": "대여가 없다고 달을 제외하면 모든 회원을 남긴다는 목표에 어긋납니다.",
    "version": "0.1.1",
    "data": {
      "members": [
        {
          "id": "m1",
          "name": "솔"
        },
        {
          "id": "m2",
          "name": "별"
        },
        {
          "id": "m3",
          "name": "달"
        }
      ],
      "loans": [
        {
          "id": "l1",
          "member_id": "m1",
          "book": "책 A"
        },
        {
          "id": "l2",
          "member_id": "m1",
          "book": "책 B"
        },
        {
          "id": "l3",
          "member_id": "m2",
          "book": "책 C"
        }
      ]
    },
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "R3",
    "type": "relation",
    "level": "전이형",
    "title": "이름이 같으면 같은 사람일까요?",
    "prompt": "솔이라는 이름의 회원 m4와 책 D 대여가 추가되었습니다. 이름 연결과 ID 연결의 행 수를 모두 예측해 보세요.",
    "mode": "duplicate",
    "expected": 7,
    "hint": "이름 솔인 회원 2명과 이름 솔로 표시된 대여 3개가 이름 기준으로 조합됩니다.",
    "explanation": "이름 기준은 솔 2명 × 솔의 대여 3개 + 별 1행 = 7행입니다. ID 기준은 각 대여가 실제 회원 1명에 연결되어 4행입니다.",
    "rubric": "동명이인으로 생긴 잘못된 조합을 짚고 ID 연결에서 4행이 되는 이유를 말한다.",
    "counter": "m4가 책 A를 빌렸다고 이름만으로 연결하면 원본 회원 ID m1과 어긋납니다.",
    "version": "0.1.1",
    "data": {
      "members": [
        {
          "id": "m1",
          "name": "솔"
        },
        {
          "id": "m2",
          "name": "별"
        },
        {
          "id": "m3",
          "name": "달"
        },
        {
          "id": "m4",
          "name": "솔"
        }
      ],
      "loans": [
        {
          "id": "l1",
          "member_id": "m1",
          "book": "책 A"
        },
        {
          "id": "l2",
          "member_id": "m1",
          "book": "책 B"
        },
        {
          "id": "l3",
          "member_id": "m2",
          "book": "책 C"
        },
        {
          "id": "l4",
          "member_id": "m4",
          "book": "책 D"
        }
      ]
    },
    "expectedVariants": {
      "base": 7,
      "id": 4
    },
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "U1",
    "type": "rule",
    "level": "안내형",
    "title": "신규 참여 기회를 늘리기",
    "prompt": "최소 2명, 그중 신규 2명 이상을 고르는 규칙을 찾아보세요. 정원 제한은 없습니다.",
    "capacity": 99,
    "extra": false,
    "hint": "2점 이상 또는 2점 이상이며 신규만을 비교해 보세요.",
    "explanation": "여러 해가 가능합니다. 1점 이상으로 모두 선택하는 규칙도 목표를 충족합니다. 선택 인원과 제외되는 사람을 비교해 보세요.",
    "rubric": "목표 충족을 확인하고 두 대안의 선택 인원·제외되는 사람·부담 차이를 설명한다.",
    "counter": "3점 이상은 신규가 나 1명뿐이므로 목표를 충족하지 못합니다.",
    "version": "0.1.1",
    "data": [
      {
        "name": "가",
        "score": 3,
        "new": false
      },
      {
        "name": "나",
        "score": 3,
        "new": true
      },
      {
        "name": "다",
        "score": 2,
        "new": true
      },
      {
        "name": "라",
        "score": 1,
        "new": true
      }
    ],
    "goal": {
      "min_total": 2,
      "min_new": 2,
      "capacity": null
    },
    "allowedRules": [
      {
        "min": 1,
        "newOnly": false
      },
      {
        "min": 1,
        "newOnly": true
      },
      {
        "min": 2,
        "newOnly": false
      },
      {
        "min": 2,
        "newOnly": true
      }
    ],
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "U2",
    "type": "rule",
    "level": "독립형",
    "title": "정원이 두 명이라면",
    "prompt": "최소 2명, 신규 2명 이상을 고르되 정원은 2명입니다.",
    "capacity": 2,
    "extra": false,
    "hint": "모두 선택하면 정원을 넘습니다. 신규 조건도 바꿔 보세요.",
    "explanation": "2점 이상이며 신규만 선택하면 나·다 2명으로 목표와 정원을 충족합니다.",
    "rubric": "신규 2명과 정원 2명을 각각 확인하고 전원 선택이 실패하는 이유를 말한다.",
    "counter": "1점 이상이며 신규만은 나·다·라 3명으로 정원을 초과합니다.",
    "version": "0.1.1",
    "data": [
      {
        "name": "가",
        "score": 3,
        "new": false
      },
      {
        "name": "나",
        "score": 3,
        "new": true
      },
      {
        "name": "다",
        "score": 2,
        "new": true
      },
      {
        "name": "라",
        "score": 1,
        "new": true
      }
    ],
    "goal": {
      "min_total": 2,
      "min_new": 2,
      "capacity": 2
    },
    "allowedRules": [
      {
        "min": 2,
        "newOnly": true
      }
    ],
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  },
  {
    "id": "U3",
    "type": "rule",
    "level": "전이형",
    "title": "데이터가 바뀌면 해도 바뀔까요?",
    "prompt": "신규 마(4점)가 추가되었습니다. 최소 2명, 신규 2명 이상, 정원 3명을 만족하는 대안 두 개를 찾아보세요.",
    "capacity": 3,
    "extra": true,
    "hint": "3점 이상과 2점 이상이며 신규만의 결과를 비교해 보세요.",
    "explanation": "3점 이상은 가·나·마, 2점 이상이며 신규만은 나·다·마입니다. 둘 다 목표를 충족하지만 제외되는 사람이 다릅니다.",
    "rubric": "서로 다른 두 해와 제외되는 사람을 비교하고 목표 충족과 공정성 판단을 구분한다.",
    "counter": "모든 신청자를 선택하면 5명으로 정원 3명을 넘습니다.",
    "version": "0.1.1",
    "data": [
      {
        "name": "가",
        "score": 3,
        "new": false
      },
      {
        "name": "나",
        "score": 3,
        "new": true
      },
      {
        "name": "다",
        "score": 2,
        "new": true
      },
      {
        "name": "라",
        "score": 1,
        "new": true
      },
      {
        "name": "마",
        "score": 4,
        "new": true
      }
    ],
    "goal": {
      "min_total": 2,
      "min_new": 2,
      "capacity": 3
    },
    "allowedRules": [
      {
        "min": 2,
        "newOnly": true
      },
      {
        "min": 3,
        "newOnly": false
      },
      {
        "min": 3,
        "newOnly": true
      }
    ],
    "review_status": {
      "calculation": "checked_in_local_prototype",
      "independent_content_review": "pending",
      "actual_user_validation": "not_performed"
    }
  }
];
  function evaluate(p, state) {
    if (p.type === "condition") return p.data.filter(x => p.mode === "boundary" ? (state.variant === "strict" ? x.score > 10 : x.score >= 10) : p.mode === "and" ? x.color === "빨강" && x.shape === "원" : x.color === "빨강" || x.shape === "원").map(x => x.id);
    if (p.type === "relation") {
      const rows = [], byName = p.mode === "duplicate" && state.variant !== "id";
      for (const member of p.data.members) {
        const loans = p.data.loans.filter(loan => byName ? p.data.members.find(x => x.id === loan.member_id)?.name === member.name : loan.member_id === member.id);
        for (const loan of loans) rows.push([p.mode === "duplicate" ? `${member.id} · ${member.name}` : member.name, loan.book + (byName && loan.member_id !== member.id ? " (잘못 연결)" : "")]);
        if (!loans.length && p.mode === "left") rows.push([member.name, "대여 없음"]);
      }
      return rows;
    }
    const selected = p.data.filter(x => x.score >= state.min && (!state.newOnly || x.new));
    const newcomers = selected.filter(x => x.new).length;
    return { selected, newcomers, ok: selected.length >= p.goal.min_total && newcomers >= p.goal.min_new && (p.goal.capacity === null || selected.length <= p.goal.capacity) };
  }
  function fresh() { return { selected: [], variant: "base", min: 3, newOnly: false, prediction: "", total: "", newcomers: "", notes: "", seen: [], rules: [], checked: false, recorded: false, hint: false }; }
  function coverage(p, a) {
    if (p.id === "C3") return a.seen.includes("base") && a.seen.includes("strict");
    if (p.id === "R3") return a.seen.includes("base") && a.seen.includes("id");
    if (p.type === "rule") return a.rules.length >= (p.id === "U3" ? 2 : 1);
    return a.seen.length > 0;
  }
  root.CoqueryPuzzles = { puzzles, evaluate, fresh, coverage };
})(globalThis);
