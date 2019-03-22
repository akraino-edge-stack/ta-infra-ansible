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

[ -n "$__AUTOCOM_LIB_LOG_INC__" ] && return || __AUTOCOM_LIB_LOG_INC__=1

LOGGING_TIMESTAMP_FORMAT='%b %d %H:%M:%S'

_logging_fmt()
{
	local fmt="%7s : ${1}%s\n"

	[ -n "${LOGGING_TIMESTAMPS}" -a "${LOGGING_TIMESTAMPS}" != "0" ] \
		&& printf -v fmt "%(${LOGGING_TIMESTAMP_FORMAT})T %s" -1 "${fmt}"

	printf "%s" "${fmt}"
}

debug()
{
	local f
	local fmt="$(_logging_fmt "${1}")"
	local src=""

	shift

	[ -n "${LOGGING_SOURCES}" -a "${LOGGING_SOURCES}" != "0" ] \
		&& src=" [${FUNCNAME[1]}()]"

	[ -n "${LOGGING_DEBUG}" ] && [ "${LOGGING_DEBUG}" -ne 0 ] \
		&& printf "${fmt}" "DEBUG" "${@}" "${src}" 1>&2

	for f in "${LOGGING_HOOKS_DEBUG[@]}" "${LOGGING_HOOKS_ALL[@]}"; do "${f}" "${@}" ; done

	return 0
}

info()
{
	local f
	local fmt="$(_logging_fmt "${1}")"
	local src=""

	shift

	[ -n "${LOGGING_SOURCES}" -a "${LOGGING_SOURCES}" != "0" ] \
		&& src=" [${FUNCNAME[1]}()]"

	( [ -z "${LOGGING_QUIET}" ] || [ "${LOGGING_QUIET}" -eq 0 ] ) \
		&& printf "${fmt}" "INFO" "${@}" "${src}"

	for f in "${LOGGING_HOOKS_INFO[@]}" "${LOGGING_HOOKS_ALL[@]}"; do "${f}" "${@}" ; done

	return 0
}

_logging_log_err()
{
	local f
	local fmt="$(_logging_fmt "${2}")"
	local src=""
	local label="${1:-ERROR}"

	shift 2

	[ -n "${LOGGING_SOURCES}" -a "${LOGGING_SOURCES}" != "0" ] \
		&& src=" [${FUNCNAME[2]}()]"

	printf "${fmt}" "${label}" "${@}" "${src}" 1>&2

	for f in $(eval "echo \"\${LOGGING_HOOKS_${label}[@]}\"") "${LOGGING_HOOKS_ALL[@]}" ; do "${f}" "${@}" ; done
}

notice()
{
	_logging_log_err NOTICE "${@}"
}

warn()
{
	_logging_log_err WARNING "${@}"
}

error()
{
	_logging_log_err ERROR "${@}"
}

alert()
{
	_logging_log_err ALERT "${@}"
}

emerg()
{
	_logging_log_err EMERG "${@}"
}

crit()
{
	_logging_log_err CRIT "${@}"
}

_main()
{
	local f="${1}"
	shift
	"${f}" "$@"
}


[ "${BASH_SOURCE}" != "${0}" ] || _main "${@}"

# Local Variables:
# mode: sh
# tab-width: 4
# End:
