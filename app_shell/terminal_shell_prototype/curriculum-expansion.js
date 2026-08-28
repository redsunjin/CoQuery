function configureExpandedCurriculum() {
  if (typeof learningPathUnits === "undefined") {
    return false;
  }

  if (!learningPathUnits.some((unit) => unit.id === "business")) {
    learningPathUnits.forEach((unit) => {
      const originalMatch = unit.match;
      if (typeof originalMatch === "function") {
        unit.match = (concepts) => !concepts.includes("business") && originalMatch(concepts);
      }
    });

    learningPathUnits.push({
      id: "business",
      ko: {
        title: "5. 업무 질문 해결하기",
        description: "여러 SQL 개념을 조합해 실제 업무형 질문에 답합니다.",
      },
      en: {
        title: "5. Solve business questions",
        description: "Combine SQL concepts to answer realistic business questions.",
      },
      match: (concepts) => concepts.includes("business"),
    });
  }

  return true;
}

function refreshExpandedCurriculum() {
  if (!configureExpandedCurriculum()) {
    return;
  }
  if (typeof refreshLearningPath === "function") {
    setTimeout(() => refreshLearningPath(), 0);
  }
}

refreshExpandedCurriculum();
