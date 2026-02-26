export default {
	'^/(api|assets|files)': {
		target: `http://localhost:8000`,
		ws: true,
		changeOrigin: true
	}
};
