import {spawn} from 'node:child_process';
const node=process.execPath;
const api=spawn(node,['backend/server.mjs'],{stdio:'inherit'});
const vite=spawn(node,['node_modules/vite/bin/vite.js'],{stdio:'inherit'});
const cleanup=()=>{api.kill();vite.kill();};
process.on('SIGINT',cleanup);process.on('SIGTERM',cleanup);
api.on('exit',code=>{if(code){console.error('API terminou com erro',code);vite.kill();}});
vite.on('exit',code=>{if(code){console.error('Vite terminou com erro',code);api.kill();}});
