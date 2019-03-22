#!/bin/bash
# vim:noet:sw=4:ts=4:ft=sh

# Copyright 2019 Nokia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[ -n "$__AUTOCOM_LIB_TMUX_INC__" ] && return || __AUTOCOM_LIB_TMUX_INC__=1

source "$(dirname "$BASH_SOURCE")/log.inc"

TMUX_SESSION_PREFIX="tmux-session-"
TMUX_TMPDIR="/tmp/tmp_console"
TMUX_SESSION="${TMUX_SESSION_PREFIX}deploy"
TMUX_LOGDIR="/var/log/ironic/console_logs/"
TMUX_RC_FILE="$(dirname "$BASH_SOURCE")/tmux.conf"

tmux_log_start()
{
	local name="$1"

	TMUX="" tmux -C -f "$TMUX_RC_FILE" \
			attach-session -t "$TMUX_SESSION" \; \
			select-window -t "$name" \; \
			pipe-pane -o "exec cat>>\"$TMUX_LOGDIR/$name.log\"" \; \
			detach &>/dev/null \
		|| crit "Failed to start logging tmux window '%s'." "$name"
}

tmux_session_env_set()
{
	local tmpdir="${1:-$TMUX_TMPDIR}"
	local session="$2"
	local name="$3"
	local value="$4"

	TMUX_TMPDIR="$tmpdir" tmux -f "$TMUX_RC_FILE" set-environment ${session:+-t "$session"} "$name" "$value" \
		|| crit "Failed to set session '%s' environment variable '%s' to '%s'." "$session" "$name" "$value"
}

tmux_env_set()
{
	tmux_session_env_set "" "$TMUX_SESSION" "$@"
}

tmux_session_env_get()
{
	local tmpdir="${1:-$TMUX_TMPDIR}"
	local session="$2"
	local name="$3"
	local output

	output="$(TMUX_TMPDIR="$tmpdir" tmux 2>/dev/null -f "$TMUX_RC_FILE" show-environment ${session:+-t "$session"} "$name")" || :

	echo "${output#$name=}"
}

tmux_env_get()
{
	tmux_session_env_get "" "$TMUX_SESSION" "$@"
}

tmux_session_start()
{
	local name="$1"
	shift

	debug "Starting new tmux session with window '%s'." "$name"

	tmux -f "$TMUX_RC_FILE" new-session -s "$TMUX_SESSION" -d -n "$name" "$(printf "'%s' " "$@")" \
		|| crit "Failed to start a new tmux session with '%s' running in it." "$name"

	tmux_log_start "$name"
}

tmux_list_sessions()
{
	local tmpdir="${1:-$TMUX_TMPDIR}"

	debug "Listing tmux sessions found from the temporary directory '%s'." "$tmpdir"

	TMUX_TMPDIR="$tmpdir" tmux ${TMUX_RC_FILE:+-f "$TMUX_RC_FILE"} list-sessions -F '#{session_name}' 2> /dev/null
}

tmux_session_is_running()
{
	tmux -f "$TMUX_RC_FILE" has-session -t "$TMUX_SESSION" &>/dev/null
}

_tmux_cmd_title_is_new()
{
	local name="$1"

	debug "Checking that a tmux window with name '%s' is not already running." "$name"

	! tmux_cmd_is_running "$name"
}

tmux_cmd_exists()
{
	local name="$1"

	debug "Checking if a command with the name '%s' exists." "$name"

	tmux_cmd_list | grep -q "^$name\$"
}

tmux_cmd_pid()
{
	local name="$1"
	local output pid

	debug "Fetching pid of tmux command '%s'." "$name"

	output="$(tmux -f "$TMUX_RC_FILE" list-windows -t "$TMUX_SESSION" -F '#{window_name}-pid=#{pane_pid}')" \
		|| crit "Failed to list tmux session's windows."

	pid="$(grep -m1 "^${name}-pid=" <<< "$output")"

	[ -n "$pid" ] || return 1

	echo "${pid##*=}"
}

tmux_cmd()
{
	local name="$1"
	shift

	debug "Executing '%s' in a new tmux window." "$name"

	! tmux_cmd_exists "$name" \
		|| crit "A command with the name '%s' already exists." "$name"

	tmux -f "$TMUX_RC_FILE" new-window -n "$name" -d "/bin/bash -c \"sleep .2 ; $(printf "'%s' " "$@") ; echo \\\"@@@@@ autocom:tmux_cmd:exit_value: \\\$? @@@@@\\\" ; sleep 1\" " \
		|| crit "Failed to execute command '%s' / '%s'." "$name" "$*"

	tmux_log_start "$name"
}

tmux_cmd_list()
{
	local name="$name"

	debug "Listing tmux commands / windows in session '%s'." "$TMUX_SESSION"

	tmux -f "$TMUX_RC_FILE" list-windows -F '#{window_name}' \
		|| crit "Failed to list tmux session's windows."
}

tmux_attach()
{
	local foreground name new_prefix

	[ "$1" != "--foreground" ] \
		|| { foreground="set-option exit-unattached on ;" ; shift ; }

	name="$1"
	new_prefix="$2"

	debug "Attaching %sto window '%s' in session '%s' with prefix '%s'." \
		"${foreground:+"with foreground option "}" "$name" "$SESSION_ID" "$new_prefix"

	tmux_cmd_exists "$name" \
		|| name=""

	tmux \
			new-session -t "$TMUX_SESSION" -s "${TMUX_SESSION/$TMUX_SESSION_PREFIX/$new_prefix}" \; \
			select-window ${name:+-t "$name"} \; \
			set status on \; \
			set destroy-unattached on \; \
			$foreground \
			set-window-option remain-on-exit off \
		|| crit "Failed to attach to session %s's window '%s' with new prefix '%s'." "$SESSION_ID" "$name" "$new_prefix"
}

tmux_cmd_assert()
{
	local delay="$1"
	shift

	tmux_cmd "$@"

	sleep "$delay"

	tmux_cmd_is_running "$1" \
		|| crit "Executing '%s' in a tmux window seems to have failed soon after starting." "$1"
}

tmux_kill_try()
{
	local name="$1"

	debug "Killing '%s' from a tmux session." "$name"

	tmux -f "$TMUX_RC_FILE" kill-window -t "$name"
}

tmux_kill()
{
	local name="$1"

	tmux_kill_try "$name" \
		|| crit "Failed to kill '%s' from the tmux session." "$name"
}

tmux_get_window_count()
{
	tmux_cmd_list | wc -l
}

tmux_cmd_is_running()
{
	local name="$1"

	debug "Checking whether '%s' is running in tmux." "$name"

	tmux -f "$TMUX_RC_FILE" list-windows -F "#{window_name}-dead=#{pane_dead}" \
		| grep -q "^$name-dead=0\$"
}

tmux_count_zombies()
{
	debug "Counting dead tmux windows."

	tmux -f "$TMUX_RC_FILE" list-windows -F "window-is-dead=#{pane_dead}" \
		| grep -c "^window-is-dead=1\$"
}

tmux_cmd_exit_status()
{
	local name="$1" e

	debug "Checking whether '%s' has returned an error." "$name"

	! tmux_cmd_is_running "$name" \
		|| crit "Cannot check if command returned an error; command is still running."

	e="$(tmux -f "$TMUX_RC_FILE" capture-pane -t "$name" -p | grep -o '@@@@@ autocom:tmux_cmd:exit_value: [0-9]\+ @@@@@' | grep -o '[0-9]\+')"

	[[ "$e" =~ ^[0-9]+$ ]] \
		|| crit "Command %s's exit status '%s' doesn't look like a number." "$name" "$e"

	return $e
}

tmux_session_init()
{
	export TMUX_TMPDIR="$1"
	export TMUX_SESSION="${TMUX_SESSION_PREFIX}$2"
	export TMUX_LOGDIR="$3"
	export TMUX_RC_FILE="$4"

	debug "Initializing tmux session '%s': tmpdir='%s', logdir='%s'" \
		"$TMUX_SESSION" "$TMUX_TMPDIR" "$TMUX_LOGDIR"

	mkdir -p "$TMUX_TMPDIR" \
		|| crit "Failed to create tmux's temporary directory '%s'." "$TMUX_TMPDIR"

	mkdir -p "$TMUX_LOGDIR" \
		|| crit "Failed to create tmux's log file directory."
}

tmux_kill_other_sessions()
{
	local session sessions

	debug "Killing other tmux sessions than '%s' (that are still related to the same autocom session)." \
		"$TMUX_SESSION"

	sessions="$(tmux_list_sessions)" \
		|| crit "Failed to get a list of sessions to kill."

	sessions="$(echo "$sessions" | grep "${TMUX_SESSION/$TMUX_SESSION_PREFIX/}")" \
		|| crit "No tmux sessions found for the running autocom session."

	sessions="$(echo "$sessions" | grep -v "$TMUX_SESSION")" \
		|| debug "No other tmux sessions in this autocom session."

	for session in $sessions
	do
		tmux -f "$TMUX_RC_FILE" kill-session -t "$session" \
			|| crit "Failed to kill tmux session '%s'." "$session"
	done
}

tmux_kill_other_windows()
{
	local name="$1"

	[ -n "$name" ] \
		&& debug "Killing all other tmux windows than '%s'." "$name" \
		|| debug "Killing all other tmux windows."

	tmux -f "$TMUX_RC_FILE" kill-window -a ${name:+-t "$name"}
}

tmux_session_uninit()
{
	local name="$1"

	debug "Uninitializing tmux session (name='%s')." "$name"

	tmux_kill_other_sessions
	tmux_kill_other_windows "$name"
}

tmux_set_alternate_prefix()
{
	local prefix="$1"

	TMUX_SESSION_PREFIX="${prefix}-"
}

# Local Variables:
# mode: sh
# tab-width: 4
# End:
