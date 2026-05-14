<script setup>
import { render } from "github-buttons";
import { onMounted, useTemplateRef } from "vue";

const anchorRef = useTemplateRef("anchor");

onMounted(() => {
  const anchor = anchorRef.value;
  render(anchor, (el) => {
    anchor.parentNode.replaceChild(el, anchor);
  });
});
</script>

<template>
  <a
    ref="anchor"
    class="github-button"
    href="https://github.com/prettier/prettier"
    data-show-count="true"
    aria-label="Star prettier on GitHub"
  >
    GitHub
  </a>
</template>
