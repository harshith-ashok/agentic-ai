<script lang="ts">
	import { marked } from 'marked';
	let rawResponse = '';
	export async function sendMessage(message: string) {
		const response = await fetch('http://localhost:8000/chat', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ message })
		});
		const text = await response.text();
		try {
			const json = JSON.parse(text);
			if (json && typeof json.reply_markdown !== 'undefined') {
				rawResponse = String(json.reply_markdown);
			} else {
				rawResponse = text;
			}
		} catch {
			rawResponse = text;
		}
	}
</script>

<input
	type="text"
	placeholder="Type a message and press Enter"
	on:keydown={async (e) => {
		if (e.key !== 'Enter') return;
		const input = e.currentTarget as HTMLInputElement;
		const msg = input.value.trim();
		if (!msg) return;
		await sendMessage(msg);
	}}
/>

{#if rawResponse}
	{@html marked(rawResponse)}
{/if}
