<script lang="tsx">
import type { VNode } from "vue";
export default {
  computed: {
    foo(): string {
      return "foo";
    },
  },
  render(h): VNode {
    return <div>{this.foo}</div>;
  },
};
</script>
