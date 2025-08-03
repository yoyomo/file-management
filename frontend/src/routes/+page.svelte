<script lang="ts">
  import { onMount } from 'svelte';

  let status = 'loading...';

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/health');
      const json = await res.json();
      status = json.status;
    } catch (e) {
      status = 'backend unreachable';
    }
  });
</script>

<h1>Backend status: {status}</h1>