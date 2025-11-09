<script lang="ts">
	import { marked } from 'marked';
	import { writable } from 'svelte/store';
	import logo from '$lib/assets/logo.svg';
	let input = '';
	let loading = false;
	let lastOutput: string = '';

	const submitMessage = async () => {
		if (!input.trim()) return;
		loading = true;

		try {
			const res = await fetch('http://127.0.0.1:8000/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					session_id: 'mysession', // You can make this dynamic
					message: input
				})
			});
			const data = await res.json();
			lastOutput = data.reply;
		} catch (err) {
			lastOutput = 'Error connecting to AI backend.';
			console.error(err);
		} finally {
			loading = false;
			input = '';
		}
	};

	// Svelte action for markdown rendering
	function markdown(node: HTMLElement, content: string) {
		node.innerHTML = marked.parse(content || '') as string;
		return {
			update(newContent: string) {
				node.innerHTML = marked.parse(newContent || '') as string;
			}
		};
	}
</script>

<div class="m-10 flex h-screen flex-col items-center justify-center bg-gray-50 px-4">
	<!-- Placeholder SVG -->
	<div class="mb-6 flex flex-col items-center">
		<img class="h-32 w-32" src={logo} alt="" />
	</div>

	<!-- AI Output Box -->
	<div
		class="mb-6 flex w-full max-w-xl items-center justify-center overflow-auto rounded-md bg-white p-4 shadow-md"
		style="min-height: 100px;"
	>
		{#if loading}
			<div class="flex items-center justify-center">
				<div class="spinner"></div>
			</div>
		{:else if lastOutput}
			<div class="prose" use:markdown={lastOutput}></div>
		{:else}
			<p class="text-center text-gray-400">Type something to begin</p>
		{/if}
	</div>

	<!-- Input Box -->
	<div class="flex w-full max-w-xl">
		<input
			type="text"
			bind:value={input}
			placeholder="Type your message..."
			class="flex-1 rounded-l-md border border-gray-300 p-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
			on:keydown={(e) => e.key === 'Enter' && submitMessage()}
		/>
		<button
			class="rounded-r-md bg-indigo-500 px-4 text-white hover:bg-indigo-600"
			on:click={submitMessage}
		>
			Send
		</button>
	</div>
</div>

<style>
	/* Simple spinner animation */
	.spinner {
		border: 4px solid rgba(0, 0, 0, 0.1);
		border-left-color: #4f46e5;
		border-radius: 50%;
		width: 3rem;
		height: 3rem;
		animation: spin 1s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
