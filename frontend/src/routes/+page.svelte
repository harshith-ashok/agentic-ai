<script lang="ts">
	let results: any[] = [];
	let errorMessage = '';

	async function search_by_tag(tag: string) {
		results = [];
		errorMessage = '';

		try {
			const response = await fetch('http://localhost:8000/search_by_tag', {
				method: 'POST',
				body: JSON.stringify({ tag }),
				headers: { 'Content-Type': 'application/json' }
			});

			const text = await response.text();

			// Try to parse JSON safely
			let json;
			try {
				json = JSON.parse(text);
			} catch (e) {
				errorMessage = 'Response was not valid JSON:\n' + text;
				return;
			}

			if (json.contexts && Array.isArray(json.contexts)) {
				results = json.contexts;
			} else {
				errorMessage = "JSON missing expected 'contexts' array.";
			}
		} catch (err) {
			errorMessage = 'Fetch failed: ' + String(err);
		}
	}
</script>

<input
	type="text"
	placeholder="Search by tag and press Enter"
	on:keydown={async (e) => {
		if (e.key !== 'Enter') return;
		const input = e.currentTarget as HTMLInputElement;
		const tag = input.value.trim();
		if (!tag) return;
		await search_by_tag(tag);
	}}
/>

<!-- Error display -->
{#if errorMessage}
	<p style="color: red">{errorMessage}</p>
{/if}

<!-- Results list -->
{#if results.length > 0}
	<ul class="list list-disc">
		{#each results as item}
			<li style="margin-bottom: 1rem;" class="list list-disc">
				<strong>Content:</strong>
				{item.content}<br />
				<strong>Tags:</strong>
				{item.tags ? item.tags.join(', ') : 'none'}<br />
			</li>
		{/each}
	</ul>
{/if}
