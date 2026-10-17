<script lang="ts">
  import { page } from '$app/state';
</script>

<h1>{page.status}</h1>
<p>{page.error?.message ?? 'The request could not be completed.'}</p>
