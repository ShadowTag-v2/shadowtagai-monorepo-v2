import { computed, inject, ref, watchEffect } from "vue";
import { type GeneralNode, highlightKey, type Pos } from "./dumpTree";

interface Props {
  node: GeneralNode;
  cursorPosition?: Pos;
}

export function useHighlightNode(props: Props) {
  const highlightContext = inject(highlightKey);
  const expanded = ref(true);

  function highlightNode() {
    const { start, end } = props.node;
    highlightContext?.([start.row, start.column, end.row, end.column]);
  }

  function withinPos({ start, end }: GeneralNode, pos?: Pos) {
    if (!pos) {
      return false;
    }
    const { row, column } = pos;
    const withinStart = start.row < row || (start.row === row && start.column <= column);
    const withinEnd = end.row > row || (end.row === row && end.column >= column);
    return withinStart && withinEnd;
  }

  const isWithin = computed(() => {
    return withinPos(props.node, props.cursorPosition);
  });
  const isTarget = computed(() => {
    if (!isWithin.value) {
      return false;
    }
    const { node, cursorPosition } = props;
    const isTarget =
      !expanded.value || // children not expanded, current target is the target
      !node.children.some((n) => withinPos(n, cursorPosition)); // no children within node
    return isTarget;
  });

  const nodeRef = ref<HTMLElement | null>(null);
  watchEffect(() => {
    if (isTarget.value) {
      nodeRef.value?.scrollIntoView({
        block: "center",
      });
    }
  });

  return {
    isTarget,
    isWithin,
    highlightNode,
    expanded,
    nodeRef,
  };
}
